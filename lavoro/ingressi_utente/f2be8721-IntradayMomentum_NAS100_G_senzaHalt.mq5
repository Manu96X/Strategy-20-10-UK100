//+------------------------------------------------------------------+
//|                        IntradayMomentum_NAS100_G_senzaHalt.mq5   |
//|  BUILD GS = build G SENZA il blocco su expectancy (29/09/2026):  |
//|   tolti HALT_TRADES_WIN e RollingExpectancyBad (somma degli      |
//|   ultimi 100 trade < 0 -> stop permanente). In challenge non     |
//|   scatta mai (< 100 trade per conto), al funded l'IM e' spento,  |
//|   e con edge intatto scatterebbe per errore (finestra da 100     |
//|   trade: z = 0,5-0,8). Blocco su drawdown 37,4R INVARIATO.       |
//|  Tutto il resto e' identico a G.  --- dalla build G: ---         |
//|  BUILD G = build F + variante H3 del protocollo F3 (validata):   |
//|   - stop protettivo a 1,5*dist invece di 2*dist, a PARITA' di    |
//|     perdita massima (2R): lotti = 2R / (1,5*dist), tetto        |
//|     nozionale 4x invariato;                                      |
//|   - guardia giornaliera = 4R (a R = 500$ resta 2.000$ come E/F).  |
//|  Tutto il resto e' identico a F (robustezza D1-D9 inclusa).      |
//|  --- dalla build F: ---                                          |
//|   D1  chiusure: nessuna richiesta a mercato chiuso, ritentativi  |
//|       a ritmo limitato, codici d'errore classificati, niente     |
//|       ciclo bloccante, tetto di richieste al giorno              |
//|   D1b prima di ogni invio: terminale, EA, conto e simbolo        |
//|   D2  riferimento del giorno e guardia persistenti ai riavvii    |
//|   D3  filtro news: allarme se il calendario MQL5 non risponde    |
//|   D4  niente PositionModify se lo stop e' gia' al livello        |
//|   D5  messaggio sulla posizione di oggi riformulato              |
//|   D6  calendario NYSE fino al 2028 (nyse.com, 27/09/2026);       |
//|       tolto il 23/12/2027, che NON e' una mezza seduta           |
//|   D8  log di fill, slippage con segno (+ = sfavorevole), spread  |
//|   D9  blocco contro due copie di F sullo stesso conto            |
//|  Build precedenti: G (IM 09-27-G), F (IM 09-27-F), E (IM 08-22-E)|
//+------------------------------------------------------------------+
#property copyright "Private"
#property version   "2.21"
#property strict
#define BUILD_ID "IM 09-29-GS"

#include <Trade/Trade.mqh>

//=============================== INPUT ==============================
input group             "== Identita' =="
input long              InpMagic             = 26082701;     // Magic number
input string            InpLogFileName       = "IM_NAS100_trades.csv"; // Log trade (Files/)

input group             "== Sessione (verificare su server FTMO!) =="
enum ENUM_DST_MODE { DST_US_ALIGNED=0, DST_EU_ALIGNED=1 };
input ENUM_DST_MODE     InpDSTMode           = DST_US_ALIGNED; // Convenzione DST del server
input int               InpSessOpenHour      = 16;            // Ora apertura cash USA (ora server)
input int               InpSessOpenMin       = 30;            // Minuto apertura
input bool              InpUseNYSECalendar   = true;          // Usa calendario NYSE integrato (festivi+mezze sedute)
input string            InpExtraSkipDates    = "";            // Date extra da saltare "yyyy.mm.dd,..." (manutenzione)

input group             "== Rischio =="
input double            InpRiskDollars       = 500.0;         // Rischio $ per trade (0.5% di 100k: validato)

input group             "== Target di fase FTMO =="
input bool              InpUsePhaseTarget    = false;         // Ferma tutto quando la fase e' superata (forward=false, challenge=true)
input double            InpPhaseTargetUSD    = 10000.0;       // Target sopra la baseline (fase 1=10000, fase 2=5000)
input double            InpTargetBufferUSD   = 0.0;           // Margine sopra il target (validato: 0 per questo sistema)
input double            InpPhaseBaseOverride = 0.0;           // 0 = baseline automatica al primo avvio (per login+magic)

input group             "== Esecuzione e verifica =="
input bool              InpDryRun            = false;         // true = OSSERVAZIONE: valuta e logga senza inviare ordini
input bool              InpDrawObjects       = false;         // Disegna bande e marker (PC si', VPS no)
input bool              InpAnchorSLToFill    = true;          // Riallinea lo stop al prezzo ESEGUITO
input bool              InpUseNewsFilter     = true;          // Blocca aperture vicino a news USD high-impact (solo live)

//================= PARAMETRI CONGELATI (validazione) ================
// Passati a const col pattern della build J ORB: stessi valori, non
// modificabili da finestra MT5 ne' dall'ottimizzatore del tester.
const int      LOOKBACK_DAYS    = 14;      // giorni per sigma
const int      MIN_SIGMA_DAYS   = 10;      // minimo giorni validi
const int      MIN_BARS_SESSION = 200;     // barre M1 minime per giorno valido
const double   COST_FILTER_MULT = 8.0;     // dist >= mult*(spread+2*slip)
const double   SLIP_ESTIMATE    = 1.0;     // slippage stimato per lato (unita' prezzo)
const double   PROTECTIVE_R     = 2.0;     // stop protettivo a -R multipli
const double   NOTIONAL_CAP_X   = 4.0;     // cap notional (x baseline)
const double   BASELINE_USD     = 100000.0;
const int      KILL_LOSSES      = 3;       // kill-switch: perdite chiuse nel giorno
const double   KILL_DAY_MULT    = 3.0;     // kill-switch giorno: -3R      (500$ -> 1500)
const double   EMERG_DAY_MULT   = 9.0;     // emergenza giorno:  -9R      (500$ -> 4500)
const double   HALT_DD_MULT     = 37.4;    // halt strategia: DD 37.4R    (500$ -> 18700 = 1.5x MaxDD backtest)
const int      NEWS_WINDOW_SEC  = 120;     // finestra news +/- secondi
const double   STOP_DIST_MULT   = 1.5;     // BUILD G: stop protettivo a 1,5*dist (era 2*dist); perdita massima
                                           // invariata = PROTECTIVE_R*R, quindi lotti = 2R/(1,5*dist). Protocollo F3, H3:
                                           // t 3,24 su 3 periodi indipendenti, altopiano 1,25-1,75, test nullo negativo
const double   GUARD_R_MULT     = 4.0;     // BUILD G: guardia equity giornaliera = 4R (= 2 stop pieni); a R = 500$
                                           // resta 2.000$ come in E/F, cresce col rischio (a 2.000$ fissi tagliava i trade)

//============ BUILD F: robustezza (attivi SOLO dal vivo) ============
const int      MARKET_IDLE_SEC  = 120;     // mercato aperto = ultimo tick VIVO piu' recente di cosi'
const int      TICK_STALE_SEC   = 60;      // tick con orario server piu' vecchio di cosi' = quotazione congelata
const int      RETRY_FAST_SEC   = 5;       // ritentativi di chiusura: i primi RETRY_FAST_N ogni 5 s,
const int      RETRY_FAST_N     = 5;
const int      RETRY_SLOW_SEC   = 60;      //   poi fino a RETRY_SLOW_N ogni 60 s,
const int      RETRY_SLOW_N     = 20;
const int      RETRY_LONG_SEC   = 600;     //   poi ogni 10 minuti (anche dopo un rifiuto definitivo)
const int      REQ_BUDGET_DAY   = 200;     // tetto di richieste al server al giorno (FTMO: iperattivita' > 2.000)
const int      LOCK_STALE_SEC   = 60;      // D9: battito piu' vecchio di cosi' = l'altra copia e' spenta
const int      CAL_LAST_YEAR    = 2028;    // D6: ultimo anno coperto dal calendario NYSE integrato

#define N_CHECKS        12
#define SLOT_MIN        30
#define FORCED_OFF      (SLOT_MIN*(N_CHECKS+1)-5)   // apertura+385' = 22:55
#define SESS_LEN        (SLOT_MIN*(N_CHECKS+1))     // 390'

//==================== CALENDARIO NYSE (da ORB build M) ==============
// BUILD F (D6): 2026-2028 riverificati sul sito NYSE il 27/09/2026. Nel 2028 il Capodanno cade di
// sabato e NON viene recuperato; il 23/12/2027 NON e' una mezza seduta (in E era segnato per errore).
string g_us_closed =
  "2019.01.01,2019.01.21,2019.02.18,2019.04.19,2019.05.27,2019.07.04,2019.09.02,2019.11.28,2019.12.25,"
  "2020.01.01,2020.01.20,2020.02.17,2020.04.10,2020.05.25,2020.07.03,2020.09.07,2020.11.26,2020.12.25,"
  "2021.01.01,2021.01.18,2021.02.15,2021.04.02,2021.05.31,2021.07.05,2021.09.06,2021.11.25,2021.12.24,"
  "2022.01.17,2022.02.21,2022.04.15,2022.05.30,2022.06.20,2022.07.04,2022.09.05,2022.11.24,2022.12.26,"
  "2023.01.02,2023.01.16,2023.02.20,2023.04.07,2023.05.29,2023.06.19,2023.07.04,2023.09.04,2023.11.23,2023.12.25,"
  "2024.01.01,2024.01.15,2024.02.19,2024.03.29,2024.05.27,2024.06.19,2024.07.04,2024.09.02,2024.11.28,2024.12.25,"
  "2025.01.01,2025.01.09,2025.01.20,2025.02.17,2025.04.18,2025.05.26,2025.06.19,2025.07.04,2025.09.01,2025.11.27,2025.12.25,"
  "2026.01.01,2026.01.19,2026.02.16,2026.04.03,2026.05.25,2026.06.19,2026.07.03,2026.09.07,2026.11.26,2026.12.25,"
  "2027.01.01,2027.01.18,2027.02.15,2027.03.26,2027.05.31,2027.06.18,2027.07.05,2027.09.06,2027.11.25,2027.12.24,"
  "2028.01.17,2028.02.21,2028.04.14,2028.05.29,2028.06.19,2028.07.04,2028.09.04,2028.11.23,2028.12.25,";
string g_us_half =   // mezze giornate (chiusura 13:00 ET): per questo sistema = niente trading
  "2019.07.03,2019.11.29,2019.12.24,2020.11.27,2020.12.24,2021.11.26,2022.11.25,"
  "2023.07.03,2023.11.24,2024.07.03,2024.11.29,2024.12.24,2025.07.03,2025.11.28,2025.12.24,"
  "2026.11.27,2026.12.24,2027.11.26,2028.07.03,2028.11.24,";

//============================ STATO =================================
CTrade   trade;
datetime g_lastM1Bar        = 0;
datetime g_curDay           = 0;
bool     g_dayReady         = false;
bool     g_daySkip          = false;
int      g_sessOpenMinToday = 0;
double   g_openPx           = 0.0;
double   g_prevClose        = 0.0;
double   g_sigma[N_CHECKS];
bool     g_checkDone[N_CHECKS];
bool     g_eodDone          = false;
bool     g_haltPrinted      = false;
bool     g_phaseDone        = false;
bool     g_keepAliveLogged  = false;
double   g_dayStartEq       = 0.0;
bool     g_dayGuardFired    = false;
string   g_gvPeakEquity     = "";
string   g_gvPhaseBase      = "";
string   g_state            = "AVVIO";

// --- BUILD F: stato di robustezza (usato solo dal vivo; nel tester F si comporta come E)
string   g_gvDayRef         = "";      // D2: equity di riferimento del giorno
string   g_gvDayRefDay      = "";      // D2: giorno a cui si riferisce
string   g_gvGuardDay       = "";      // D2: giorno in cui e' scattata la guardia
string   g_gvReqCount       = "";      // D1: richieste inviate oggi
string   g_gvReqDay         = "";      // D1: giorno del contatore
string   g_gvLockOwner      = "";      // D9: copia che possiede il blocco
string   g_gvLockBeat       = "";      // D9: battito della copia proprietaria
ulong    g_lastTickMs       = 0;       // D1: ultimo tick vivo (orologio locale monotono)
bool     g_closePending     = false;   // D1: chiusura richiesta e non ancora riuscita
string   g_closeWhy         = "";
int      g_closeFails       = 0;
ulong    g_nextCloseMs      = 0;
ulong    g_permUntilMs      = 0;       // D1: pausa dopo un rifiuto definitivo del server
int      g_closeState       = 0;       // D1: ultimo stato di attesa registrato nel log
datetime g_reqDay           = 0;
int      g_reqCount         = 0;
bool     g_budgetAlarm      = false;
bool     g_calOk            = true;    // D3: calendario MQL5 raggiungibile
bool     g_calChecked       = false;
int      g_newsBlocked      = 0;       // D3: ingressi bloccati dal filtro news (oggi)
double   g_lockToken        = 0.0;     // D9
bool     g_duplicate        = false;   // D9: un'altra copia attiva sullo stesso conto e magic

//====================================================================
//  UTILITA'
//====================================================================
datetime DayStart(datetime t) { return (datetime)(((long)t/86400)*86400); }

bool DateInList(const string &list, datetime day)
{
   string d = TimeToString(day, TIME_DATE);
   return (StringFind(list, d) >= 0);
}

bool InDSTMismatch(datetime day)
{
   static const string mm[][2] = {
      {"2025.03.09","2025.03.30"},{"2025.10.26","2025.11.02"},
      {"2026.03.08","2026.03.29"},{"2026.10.25","2026.11.01"},
      {"2027.03.14","2027.03.28"},{"2027.10.31","2027.11.07"},
      {"2028.03.12","2028.03.26"},{"2028.10.29","2028.11.05"}
   };
   for(int i=0;i<ArrayRange(mm,0);i++)
      if(day>=StringToTime(mm[i][0]) && day<StringToTime(mm[i][1])) return true;
   return false;
}

int SessOpenMinutes(datetime day)
{
   int base = InpSessOpenHour*60 + InpSessOpenMin;
   if(InpDSTMode==DST_EU_ALIGNED && InDSTMismatch(day)) return base-60;
   return base;
}

bool IsSkipDate(datetime day)
{
   if(InpUseNYSECalendar && (DateInList(g_us_closed,day) || DateInList(g_us_half,day))) return true;
   if(StringLen(InpExtraSkipDates)>0 && DateInList(InpExtraSkipDates,day)) return true;
   return false;
}

// FIX1 — giorno (00:00 server) della posizione aperta di questo EA; 0 se nessuna
datetime MyPositionDay()
{
   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong t = PositionGetTicket(i);
      if(PositionGetString(POSITION_SYMBOL)==_Symbol && PositionGetInteger(POSITION_MAGIC)==InpMagic)
         return DayStart((datetime)PositionGetInteger(POSITION_TIME));
   }
   return 0;
}

//====================================================================
//  BUILD F — D1/D1b: mercato aperto, permessi, ritmo e budget richieste
//====================================================================
// Il mercato e' aperto se e' arrivato da poco un tick VIVO (orario server recente), misurato con
// l'orologio locale monotono: TimeCurrent() non avanza senza tick e nella pausa 23:49-01:05 o nel
// weekend un'uscita a orario ritenterebbe a vuoto. Nel tester e' sempre aperto.
bool MarketOpenNow()
{
   if(MQLInfoInteger(MQL_TESTER)) return true;
   if(g_lastTickMs==0) return false;
   return (GetTickCount64()-g_lastTickMs < (ulong)MARKET_IDLE_SEC*1000);
}

void NoteTick()
{
   if(MQLInfoInteger(MQL_TESTER)) return;
   MqlTick tk;
   if(!SymbolInfoTick(_Symbol, tk)) return;
   if((long)TimeTradeServer()-(long)tk.time <= TICK_STALE_SEC)   // quotazione congelata alla riconnessione: non conta
      g_lastTickMs = GetTickCount64();
}

// Pre-volo: trading possibile su terminale, EA, conto e simbolo (trappola T18 del dossier).
bool TradePermitted(bool forClose, string &why)
{
   if(MQLInfoInteger(MQL_TESTER)) return true;
   if(TerminalInfoInteger(TERMINAL_CONNECTED)==0)       { why="terminale non connesso al server"; return false; }
   if(TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)==0)   { why="pulsante Algo Trading spento"; return false; }
   if(MQLInfoInteger(MQL_TRADE_ALLOWED)==0)             { why="trading automatico non consentito nelle proprieta' dell'EA"; return false; }
   if(AccountInfoInteger(ACCOUNT_TRADE_ALLOWED)==0)     { why="trading disabilitato sul conto (es. challenge chiusa)"; return false; }
   if(AccountInfoInteger(ACCOUNT_TRADE_EXPERT)==0)      { why="il conto non consente gli EA"; return false; }
   long mode = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE);
   if(mode==SYMBOL_TRADE_MODE_DISABLED)                 { why="simbolo non negoziabile"; return false; }
   if(!forClose && mode!=SYMBOL_TRADE_MODE_FULL)        { why="simbolo in sola chiusura"; return false; }
   return true;
}

// Ritentativi a ritmo limitato, sull'orologio locale monotono.
bool RetryAllowed(ulong &nextMs, int fails)
{
   ulong now = GetTickCount64();
   if(now < nextMs) return false;
   int wait = (fails < RETRY_FAST_N ? RETRY_FAST_SEC : (fails < RETRY_SLOW_N ? RETRY_SLOW_SEC : RETRY_LONG_SEC));
   nextMs = now + (ulong)wait*1000;
   return true;
}

// Rifiuti che non si risolvono ritentando: conto/terminale/server che non consentono il trading.
bool IsPermanentRetcode(uint rc)
{
   return (rc==TRADE_RETCODE_TRADE_DISABLED || rc==TRADE_RETCODE_SERVER_DISABLES_AT ||
           rc==TRADE_RETCODE_CLIENT_DISABLES_AT || rc==TRADE_RETCODE_ONLY_REAL);
}

// Budget giornaliero di richieste al server, persistente ai riavvii (GlobalVariable).
void BudgetRoll()
{
   datetime d = DayStart(TimeTradeServer());
   if(d==g_reqDay) return;
   g_reqDay = d;
   g_reqCount = 0;
   g_budgetAlarm = false;
   if(GlobalVariableCheck(g_gvReqDay) && (datetime)GlobalVariableGet(g_gvReqDay)==d && GlobalVariableCheck(g_gvReqCount))
      g_reqCount = (int)GlobalVariableGet(g_gvReqCount);
}

bool RequestBudgetOk()
{
   if(MQLInfoInteger(MQL_TESTER)) return true;
   BudgetRoll();
   if(g_reqCount < REQ_BUDGET_DAY) return true;
   if(!g_budgetAlarm)
   {
      g_budgetAlarm = true;
      PrintFormat("[IM] *** ATTENZIONE: %d richieste al server oggi: nuove richieste sospese fino a domani. Lo stop protettivo resta sul server. ***",
                  g_reqCount);
   }
   return false;
}

void CountRequest()
{
   if(MQLInfoInteger(MQL_TESTER)) return;
   BudgetRoll();
   g_reqCount++;
   GlobalVariableSet(g_gvReqDay, (double)g_reqDay);
   GlobalVariableSet(g_gvReqCount, (double)g_reqCount);
   GlobalVariablesFlush();
}

//====================================================================
//  BUILD F — D2: riferimento del giorno e guardia persistenti
//====================================================================
// Semantica di E: il riferimento e' l'equity alla PRIMA preparazione del giorno (16:30). E la
// ricalcolava a ogni reinizializzazione (rilievo R1): qui si salva la prima volta e si rilegge dopo.
void DayReferenceLoadOrSet(datetime day)
{
   if(MQLInfoInteger(MQL_TESTER))                 // nel tester: esattamente come E (nessun riavvio da proteggere)
   {
      g_dayGuardFired = false;
      g_dayStartEq = AccountInfoDouble(ACCOUNT_EQUITY);
      return;
   }
   if(GlobalVariableCheck(g_gvDayRefDay) && (datetime)GlobalVariableGet(g_gvDayRefDay)==day &&
      GlobalVariableCheck(g_gvDayRef))
   {
      g_dayStartEq = GlobalVariableGet(g_gvDayRef);
      PrintFormat("[IM] riferimento del giorno ripreso dopo il riavvio: %.2f (equity ora %.2f)",
                  g_dayStartEq, AccountInfoDouble(ACCOUNT_EQUITY));
   }
   else
   {
      g_dayStartEq = AccountInfoDouble(ACCOUNT_EQUITY);
      GlobalVariableSet(g_gvDayRefDay, (double)day);
      GlobalVariableSet(g_gvDayRef, g_dayStartEq);
      GlobalVariablesFlush();
   }
   g_dayGuardFired = (GlobalVariableCheck(g_gvGuardDay) && (datetime)GlobalVariableGet(g_gvGuardDay)==day);
}

void MarkGuardFired(datetime day)
{
   g_dayGuardFired = true;
   if(MQLInfoInteger(MQL_TESTER)) return;
   GlobalVariableSet(g_gvGuardDay, (double)day);
   GlobalVariablesFlush();
}

//====================================================================
//  BUILD F — D3: il calendario MQL5 risponde? (solo dal vivo)
//====================================================================
void CheckCalendar()
{
   if(MQLInfoInteger(MQL_TESTER) || !InpUseNewsFilter) return;
   MqlCalendarValue v[];
   datetime now = TimeTradeServer();
   ResetLastError();
   int n = CalendarValueHistory(v, now-7*86400, now+86400, NULL, "USD");
   int err = GetLastError();
   bool ok = (n > 0);
   if(!g_calChecked || ok!=g_calOk)
   {
      if(ok) PrintFormat("[IM] filtro news ATTIVO: calendario MQL5 raggiungibile (%d eventi USD in 8 giorni)", n);
      else   PrintFormat("[IM] *** ATTENZIONE: calendario MQL5 NON disponibile (eventi %d, errore %d): filtro news INATTIVO. Abilitare il calendario nel terminale. ***",
                         n, err);
   }
   g_calOk = ok;
   g_calChecked = true;
}

//====================================================================
//  BUILD F — D9: una sola copia di F per conto e magic (solo dal vivo)
//====================================================================
void LockInit()
{
   if(MQLInfoInteger(MQL_TESTER)) return;
   g_lockToken = (double)(ChartID() % 1000000000) * 1000000.0 + (double)(GetMicrosecondCount() % 1000000);
   if(GlobalVariableCheck(g_gvLockOwner) && GlobalVariableCheck(g_gvLockBeat) &&
      GlobalVariableGet(g_gvLockOwner)!=g_lockToken &&
      (double)TimeLocal()-GlobalVariableGet(g_gvLockBeat) < LOCK_STALE_SEC)
   {
      g_duplicate = true;
      PrintFormat("[IM] *** ATTENZIONE: un'altra copia di questo EA (magic %I64d) e' gia' attiva su questo conto: questa copia resta INATTIVA. Toglierla dal grafico. ***",
                  InpMagic);
      return;
   }
   LockBeat();
}

void LockBeat()
{
   if(MQLInfoInteger(MQL_TESTER)) return;
   bool foreignFresh = (GlobalVariableCheck(g_gvLockOwner) && GlobalVariableCheck(g_gvLockBeat) &&
                        GlobalVariableGet(g_gvLockOwner)!=g_lockToken &&
                        (double)TimeLocal()-GlobalVariableGet(g_gvLockBeat) < LOCK_STALE_SEC);
   if(g_duplicate)
   {
      if(foreignFresh) return;                                   // l'altra copia e' viva: resto inattiva
      g_duplicate = false;                                       // l'altra copia si e' spenta: subentro
      Print("[IM] l'altra copia non da' piu' segni di vita: questa copia diventa ATTIVA");
   }
   else if(foreignFresh && GlobalVariableGet(g_gvLockOwner) < g_lockToken)
   {
      g_duplicate = true;                                        // avvio simultaneo: vince il gettone minore
      PrintFormat("[IM] *** ATTENZIONE: due copie di questo EA (magic %I64d) sullo stesso conto: questa resta INATTIVA. ***", InpMagic);
      return;
   }
   GlobalVariableSet(g_gvLockOwner, g_lockToken);
   GlobalVariableSet(g_gvLockBeat, (double)TimeLocal());
}

void LockRelease()
{
   if(MQLInfoInteger(MQL_TESTER) || g_duplicate) return;
   if(GlobalVariableCheck(g_gvLockOwner) && GlobalVariableGet(g_gvLockOwner)==g_lockToken)
   {
      GlobalVariableDel(g_gvLockOwner);
      GlobalVariableDel(g_gvLockBeat);
      GlobalVariablesFlush();
   }
}

//====================================================================
//  COSTRUZIONE GIORNATA (logica identica alla build A)
//====================================================================
int SessionBars(datetime day, int sessMin, MqlRates &out[])
{
   datetime from = day + sessMin*60;
   datetime to   = day + (sessMin+SESS_LEN)*60 - 1;
   ArrayFree(out);
   int n = CopyRates(_Symbol, PERIOD_M1, from, to, out);
   return (n>0 ? n : 0);
}

bool ValidSessionDay(datetime day, int sessMin, MqlRates &bars[])
{
   int n = SessionBars(day, sessMin, bars);
   if(n < MIN_BARS_SESSION) return false;
   if(bars[0].time > day + (sessMin+5)*60) return false;
   return true;
}

double PriceAt(const MqlRates &bars[], int n, datetime tau)
{
   double p = EMPTY_VALUE;
   for(int i=0;i<n;i++){ if(bars[i].time<tau) p=bars[i].close; else break; }
   return p;
}

void DrawBands(datetime day)
{
   if(!InpDrawObjects) return;
   ObjectsDeleteAll(0, "IMB_");
   double aHi = MathMax(g_openPx, g_prevClose);
   double aLo = MathMin(g_openPx, g_prevClose);
   for(int k=0;k<N_CHECKS;k++)
   {
      if(g_sigma[k]==EMPTY_VALUE) continue;
      datetime t1 = day + (g_sessOpenMinToday + SLOT_MIN*k + 5)*60;
      datetime t2 = day + (g_sessOpenMinToday + SLOT_MIN*(k+1))*60;
      double ub = aHi*(1.0+g_sigma[k]), lb = aLo*(1.0-g_sigma[k]);
      string nu = StringFormat("IMB_U_%d",k), nl = StringFormat("IMB_L_%d",k);
      ObjectCreate(0,nu,OBJ_TREND,0,t1,ub,t2,ub);
      ObjectCreate(0,nl,OBJ_TREND,0,t1,lb,t2,lb);
      ObjectSetInteger(0,nu,OBJPROP_COLOR,clrDodgerBlue);
      ObjectSetInteger(0,nl,OBJPROP_COLOR,clrTomato);
      ObjectSetInteger(0,nu,OBJPROP_RAY_RIGHT,false);
      ObjectSetInteger(0,nl,OBJPROP_RAY_RIGHT,false);
   }
}

bool PrepareDay(datetime day)
{
   g_dayReady=false; g_daySkip=false; g_phaseDone=false; g_keepAliveLogged=false;
   DayReferenceLoadOrSet(day);                   // BUILD F (D2): era g_dayGuardFired=false; g_dayStartEq=equity
   ArrayInitialize(g_checkDone,false);
   g_eodDone=false;
   g_newsBlocked=0;
   CheckCalendar();                              // BUILD F (D3): solo dal vivo

   if(IsSkipDate(day))
   { g_daySkip=true; g_state="GIORNO SALTATO (calendario)"; PrintFormat("[IM] %s: festivo/mezza seduta -> nessun trading", TimeToString(day,TIME_DATE)); return false; }

   g_sessOpenMinToday = SessOpenMinutes(day);

   double moves[N_CHECKS][60];
   int    cnt[N_CHECKS];  ArrayInitialize(cnt,0);
   int found=0; double prevClose=EMPTY_VALUE;

   for(int back=1; back<=LOOKBACK_DAYS*3 && found<LOOKBACK_DAYS; back++)
   {
      datetime d = day - back*86400;
      if(IsSkipDate(d)) continue;                 // coerenza: i giorni saltati non alimentano sigma
      MqlRates bars[];
      int sm = SessOpenMinutes(d);
      if(!ValidSessionDay(d, sm, bars)) continue;
      int n = ArraySize(bars);
      double o = bars[0].open;
      if(prevClose==EMPTY_VALUE) prevClose = bars[n-1].close;
      for(int k=0;k<N_CHECKS;k++)
      {
         datetime tau = d + (sm + SLOT_MIN*(k+1))*60;
         double p = PriceAt(bars,n,tau);
         moves[k][found] = (p!=EMPTY_VALUE && o>0.0)? MathAbs(p/o-1.0) : EMPTY_VALUE;
         if(moves[k][found]!=EMPTY_VALUE) cnt[k]++;
      }
      found++;
   }
   if(found<MIN_SIGMA_DAYS || prevClose==EMPTY_VALUE)
   { g_daySkip=true; g_state="STORIA INSUFFICIENTE"; PrintFormat("[IM] %s: storia insufficiente (%d giorni)", TimeToString(day,TIME_DATE), found); return false; }

   for(int k=0;k<N_CHECKS;k++)
   {
      double s=0; int c=0;
      for(int j=0;j<found;j++) if(moves[k][j]!=EMPTY_VALUE){ s+=moves[k][j]; c++; }
      g_sigma[k] = (c<MIN_SIGMA_DAYS)? EMPTY_VALUE : s/c;
   }
   g_prevClose = prevClose;

   MqlRates tb[];
   int nt = CopyRates(_Symbol, PERIOD_M1, day+g_sessOpenMinToday*60, day+(g_sessOpenMinToday+5)*60, tb);
   if(nt<=0) return false;
   if(tb[0].time > day+(g_sessOpenMinToday+5)*60) return false;
   g_openPx = tb[0].open;

   g_dayReady = true; g_state = InpDryRun? "DRY RUN (nessun ordine)" : "ATTIVO";
   DrawBands(day);
   PrintFormat("[IM] %s pronto (%s): open=%.1f prevClose=%.1f sig17=%.3f%%",
               TimeToString(day,TIME_DATE), BUILD_ID, g_openPx, g_prevClose,
               (g_sigma[0]==EMPTY_VALUE?0:g_sigma[0]*100));
   return true;
}

//====================================================================
//  CONTABILITA' (identica alla build A)
//====================================================================
void DayStats(datetime day, double &dayPnl, int &nLosses)
{
   dayPnl=0.0; nLosses=0;
   if(!HistorySelect(day, TimeTradeServer()+60)) return;
   int nd=HistoryDealsTotal();
   long ids[]; double nets[]; int m=0;
   ArrayResize(ids,nd); ArrayResize(nets,nd);
   for(int i=0;i<nd;i++)
   {
      ulong t=HistoryDealGetTicket(i);
      if(HistoryDealGetInteger(t,DEAL_MAGIC)!=InpMagic) continue;
      if(HistoryDealGetString(t,DEAL_SYMBOL)!=_Symbol) continue;
      long pid=HistoryDealGetInteger(t,DEAL_POSITION_ID);
      double v=HistoryDealGetDouble(t,DEAL_PROFIT)+HistoryDealGetDouble(t,DEAL_COMMISSION)+HistoryDealGetDouble(t,DEAL_SWAP);
      int j; for(j=0;j<m;j++) if(ids[j]==pid) break;
      if(j==m){ ids[m]=pid; nets[m]=0.0; m++; }
      nets[j]+=v;
   }
   for(int j=0;j<m;j++)
   {
      bool closed=false;
      for(int i=0;i<nd;i++)
      {
         ulong t=HistoryDealGetTicket(i);
         if(HistoryDealGetInteger(t,DEAL_POSITION_ID)!=ids[j]) continue;
         long e=HistoryDealGetInteger(t,DEAL_ENTRY);
         if(e==DEAL_ENTRY_OUT || e==DEAL_ENTRY_OUT_BY){ closed=true; break; }
      }
      if(!closed) continue;
      dayPnl += nets[j];
      if(nets[j]<0.0) nLosses++;
   }
}

bool StrategyHalted()
{
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   double peak = GlobalVariableCheck(g_gvPeakEquity)? GlobalVariableGet(g_gvPeakEquity) : eq;
   if(eq>peak){ peak=eq; GlobalVariableSet(g_gvPeakEquity, peak); }
   double haltDD = HALT_DD_MULT * InpRiskDollars;
   if(peak-eq > haltDD)
   { if(!g_haltPrinted){ PrintFormat("[IM] HALT: drawdown %.0f$ > %.0f$", peak-eq, haltDD); g_haltPrinted=true; } g_state="HALT (drawdown)"; return true; }
   // BUILD GS: tolto il blocco su expectancy (ultimi 100 trade < 0), vedi intestazione
   return false;
}

// F5 — baseline di fase per login+magic; target su BALANCE (chiuso)
double PhaseBaseline()
{
   if(InpPhaseBaseOverride>0) return InpPhaseBaseOverride;
   if(GlobalVariableCheck(g_gvPhaseBase)) return GlobalVariableGet(g_gvPhaseBase);
   double b = AccountInfoDouble(ACCOUNT_BALANCE);
   GlobalVariableSet(g_gvPhaseBase, b);
   PrintFormat("[IM] baseline di fase registrata: %.2f (%s)", b, g_gvPhaseBase);
   return b;
}

bool PhaseTargetReached()
{
   if(!InpUsePhaseTarget) return false;
   double bal = AccountInfoDouble(ACCOUNT_BALANCE);
   if(bal >= PhaseBaseline() + InpPhaseTargetUSD + InpTargetBufferUSD)
   {
      if(!g_phaseDone) PrintFormat("[IM] FASE SUPERATA: balance %.2f >= target. Nessun nuovo trade.", bal);
      g_phaseDone=true; g_state="FASE SUPERATA";
      return true;
   }
   return false;
}

//====================================================================
//  NEWS FILTER (identico alla build A)
//====================================================================
bool NewsBlock(datetime now)
{
   if(!InpUseNewsFilter) return false;
   if(MQLInfoInteger(MQL_TESTER)) return false;
   MqlCalendarValue vals[];
   datetime from = now - NEWS_WINDOW_SEC - 60;
   datetime to   = now + NEWS_WINDOW_SEC + 60;
   int n = CalendarValueHistory(vals, from, to, NULL, "USD");
   if(n<=0) return false;
   for(int i=0;i<n;i++)
   {
      MqlCalendarEvent ev;
      if(!CalendarEventById(vals[i].event_id, ev)) continue;
      if(ev.importance != CALENDAR_IMPORTANCE_HIGH) continue;
      if(MathAbs((long)vals[i].time - (long)now) <= NEWS_WINDOW_SEC) return true;
   }
   return false;
}

//====================================================================
//  ESECUZIONE
//====================================================================
bool HasPosition()
{
   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong t=PositionGetTicket(i);
      if(PositionGetString(POSITION_SYMBOL)==_Symbol && PositionGetInteger(POSITION_MAGIC)==InpMagic)
         return true;
   }
   return false;
}

// Percorso di chiusura della build E, INVARIATO. BUILD F: usato SOLO nel tester, dove garantisce
// che il backtest di F sia identico a quello di E (stesse chiamate, stessa sequenza).
bool ClosePositionRetryE(string why)
{
   for(int k=0;k<5;k++)
   {
      if(!HasPosition()) return true;
      for(int i=PositionsTotal()-1;i>=0;i--)
      {
         ulong t=PositionGetTicket(i);
         if(PositionGetString(POSITION_SYMBOL)!=_Symbol || PositionGetInteger(POSITION_MAGIC)!=InpMagic) continue;
         trade.PositionClose(t);
      }
      Sleep(500);
   }
   bool ok=!HasPosition();
   PrintFormat("[IM] chiusura %s (%s)", ok?"eseguita":"FALLITA", why);
   return ok;
}

void CloseStateLog(int state, string msg)
{
   if(state==g_closeState) return;
   g_closeState = state;
   PrintFormat("[IM] chiusura in attesa (%s): %s", g_closeWhy, msg);
}

void CloseDone()
{
   g_closePending = false;
   g_closeWhy     = "";
   g_closeFails   = 0;
   g_nextCloseMs  = 0;
   g_closeState   = 0;
}

// BUILD F (D1) — chiusura NON bloccante dal vivo: un solo tentativo per chiamata, e solo se il
// mercato e' aperto, il trading e' consentito, il ritmo e il budget lo permettono. Se non riesce resta
// "in attesa" e viene ripresa da OnTimer (15 s) e dal primo tick utile. Ritorna true se non c'e' piu'
// la posizione.
bool CloseMyPosition(string why)
{
   if(MQLInfoInteger(MQL_TESTER)) return ClosePositionRetryE(why);
   if(!HasPosition())
   {
      if(g_closePending)
         PrintFormat("[IM] posizione non piu' presente (%s): chiusa dal server o dalla richiesta precedente", g_closeWhy);
      CloseDone();
      return true;
   }
   if(!g_closePending)
   {
      g_closePending = true; g_closeWhy = why; g_closeFails = 0; g_nextCloseMs = 0; g_closeState = 0;
   }
   string reason = "";
   if(!MarketOpenNow())              { CloseStateLog(1, "mercato chiuso o nessun tick vivo: chiudo al primo tick utile"); return false; }
   if(!TradePermitted(true, reason)) { CloseStateLog(2, "trading non consentito: " + reason); return false; }
   if(GetTickCount64() < g_permUntilMs) { CloseStateLog(5, "pausa dopo un rifiuto definitivo del server"); return false; }
   if(!RetryAllowed(g_nextCloseMs, g_closeFails)) return false;
   if(!RequestBudgetOk())            { CloseStateLog(3, "budget giornaliero di richieste esaurito"); return false; }

   uint rc = 0;
   bool sent = false;
   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong t=PositionGetTicket(i);
      if(PositionGetString(POSITION_SYMBOL)!=_Symbol || PositionGetInteger(POSITION_MAGIC)!=InpMagic) continue;
      CountRequest();
      trade.PositionClose(t);
      rc = trade.ResultRetcode();
      sent = true;
      break;                                   // una richiesta per chiamata (l'EA ha al massimo una posizione)
   }
   if(!sent) { CloseDone(); return true; }
   if(rc==TRADE_RETCODE_DONE || rc==TRADE_RETCODE_DONE_PARTIAL || rc==TRADE_RETCODE_PLACED ||
      rc==TRADE_RETCODE_POSITION_CLOSED)
   {
      for(int k=0; k<20 && HasPosition(); k++) Sleep(50);          // cache del terminale (trappola 5.14): max 1 s
      if(!HasPosition())
      {
         PrintFormat("[IM] chiusura eseguita (%s)", g_closeWhy);
         CloseDone();
         return true;
      }
      CloseStateLog(4, "richiesta accettata ma posizione ancora visibile: ricontrollo al prossimo giro");
      return false;
   }
   g_closeFails++;
   string nextTxt = "";
   if(rc==TRADE_RETCODE_MARKET_CLOSED)
   { g_lastTickMs = 0; nextTxt = "al primo tick nuovo"; }                // mercato chiuso: aspetta un tick nuovo
   else if(IsPermanentRetcode(rc))
   { g_permUntilMs = GetTickCount64() + (ulong)RETRY_LONG_SEC*1000; nextTxt = StringFormat("fra %d s (rifiuto definitivo)", RETRY_LONG_SEC); }
   else
   {
      ulong nowMs = GetTickCount64();
      nextTxt = StringFormat("fra %d s", g_nextCloseMs > nowMs ? (int)((g_nextCloseMs - nowMs)/1000) : 0);
   }
   if(g_closeFails==1 || g_closeFails%10==0)
      PrintFormat("[IM] chiusura FALLITA (%s) retcode=%u %s | tentativi %d, prossimo %s",
                  g_closeWhy, rc, trade.ResultRetcodeDescription(), g_closeFails, nextTxt);
   return false;
}

double LotsFromDpp(double dpp)
{
   double tickVal=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_VALUE);
   double tickSz =SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE);
   if(tickVal<=0||tickSz<=0) return 0.0;
   double lots = dpp / (tickVal/tickSz);
   double step=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP);
   double vmin=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN);
   double vmax=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX);
   lots = MathFloor(lots/step)*step;
   if(lots<vmin) return 0.0;
   if(lots>vmax) lots=vmax;
   return NormalizeDouble(lots,2);
}

// F4 — riallinea lo stop al fill reale; senza TP la PositionModify passa 0.0
void AnchorStopToFill(int side, double dist, double sprSignal)
{
   if(!InpAnchorSLToFill) return;
   // FIX 5.14 (BUILD E) - stesso fix della build P dell'ORB: dopo OrderSend la
   // posizione puo' non essere ancora nella cache del terminale. Senza questa
   // attesa il ciclo qui sotto non trova nulla ed esce SENZA STAMPARE NIENTE:
   // lo stop protettivo resta ancorato al prezzo RICHIESTO invece che a quello
   // ESEGUITO. Inerte in backtest: nel tester la posizione c'e' subito e la
   // guardia MQL_TESTER esclude comunque il ramo.
   if(!MQLInfoInteger(MQL_TESTER) && !HasPosition())
   {
      for(int kWait=0; kWait<20 && !HasPosition(); kWait++) Sleep(50);
      if(!HasPosition())
      { Print("[IM] *** ATTENZIONE: posizione NON leggibile dopo l'invio -> SL NON riancorato al fill. ***"); return; }
   }
   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong tk=PositionGetTicket(i);
      if(PositionGetString(POSITION_SYMBOL)!=_Symbol || PositionGetInteger(POSITION_MAGIC)!=InpMagic) continue;
      double fill = PositionGetDouble(POSITION_PRICE_OPEN);
      double slNew = NormalizeDouble(fill - side*STOP_DIST_MULT*dist, _Digits);      // BUILD G
      double slCur = PositionGetDouble(POSITION_SL);
      double reqPx = trade.RequestPrice();
      double slip  = side*(fill-reqPx);                  // BUILD F (D8): + = sfavorevole
      if(!MQLInfoInteger(MQL_TESTER))
         PrintFormat("[IM] fill %.2f | richiesto %.2f | slippage %+.2f pt (+ = sfavorevole) | spread al segnale %.2f",
                     fill, reqPx, slip, sprSignal);
      double tickSz = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
      if(tickSz<=0) tickSz=_Point;
      if(MathAbs(slNew-slCur) < 0.5*tickSz) return;      // BUILD F (D4): stop gia' al livello, niente richiesta
      double stopsLvl=(double)SymbolInfoInteger(_Symbol,SYMBOL_TRADE_STOPS_LEVEL)*_Point;
      double refPx = (side>0? SymbolInfoDouble(_Symbol,SYMBOL_BID) : SymbolInfoDouble(_Symbol,SYMBOL_ASK));
      bool okDist = (side>0? (refPx-slNew) : (slNew-refPx)) > stopsLvl;
      if(!okDist) return;
      if(!RequestBudgetOk()) return;
      CountRequest();
      if(trade.PositionModify(tk, slNew, 0.0))
         PrintFormat("[IM] SL riancorato al fill %.2f: %.2f -> %.2f (slippage %+.2f pt, + = sfavorevole)", fill, slCur, slNew, slip);
      return;
   }
}

void TryEnter(int side, double p, double band, datetime now)
{
   double dist = (side>0? p-band : band-p);
   double spread=(double)SymbolInfoInteger(_Symbol,SYMBOL_SPREAD)*_Point;
   double rtCost = spread + 2.0*SLIP_ESTIMATE;
   if(dist < COST_FILTER_MULT*rtCost) return;
   if(NewsBlock(now)){ g_newsBlocked++; Print("[IM] entry bloccata da news filter"); return; }

   double dpp = MathMin(PROTECTIVE_R*InpRiskDollars/(STOP_DIST_MULT*dist), NOTIONAL_CAP_X*BASELINE_USD/p);   // BUILD G
   double lots = LotsFromDpp(dpp);
   if(lots<=0){ Print("[IM] size sotto il minimo, trade saltato"); return; }

   if(InpDryRun)   // F2
   {
      PrintFormat("[DRY] %s lots=%.2f p=%.1f banda=%.1f dist=%.1f spread=%.2f",
                  side>0?"LONG":"SHORT", lots, p, band, dist, spread);
      return;
   }

   // BUILD F (D1b): prima dell'invio, permessi, pausa dopo rifiuto definitivo e budget (solo dal vivo)
   string why = "";
   if(!TradePermitted(false, why)) { PrintFormat("[IM] ingresso %s NON inviato: %s", side>0?"LONG":"SHORT", why); return; }
   if(!MQLInfoInteger(MQL_TESTER) && GetTickCount64() < g_permUntilMs)
   { PrintFormat("[IM] ingresso %s NON inviato: pausa dopo un rifiuto definitivo del server", side>0?"LONG":"SHORT"); return; }
   if(!RequestBudgetOk()) return;

   double stopsLvl=(double)SymbolInfoInteger(_Symbol,SYMBOL_TRADE_STOPS_LEVEL)*_Point;
   double ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
   double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID);
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints((int)MathRound(2*SLIP_ESTIMATE/_Point));
   bool ok=false;
   CountRequest();
   if(side>0)
   {
      double sl=NormalizeDouble(ask-STOP_DIST_MULT*dist,_Digits);                  // BUILD G
      if(ask-sl<stopsLvl) sl=NormalizeDouble(ask-stopsLvl-_Point,_Digits);
      ok=trade.Buy(lots,_Symbol,0.0,sl,0.0,BUILD_ID);
   }
   else
   {
      double sl=NormalizeDouble(bid+STOP_DIST_MULT*dist,_Digits);                  // BUILD G
      if(sl-bid<stopsLvl) sl=NormalizeDouble(bid+stopsLvl+_Point,_Digits);
      ok=trade.Sell(lots,_Symbol,0.0,sl,0.0,BUILD_ID);
   }
   if(!ok)
   {
      uint rc = trade.ResultRetcode();
      PrintFormat("[IM] entry fallita retcode=%d", rc);
      if(!MQLInfoInteger(MQL_TESTER) && IsPermanentRetcode(rc))
         g_permUntilMs = GetTickCount64() + (ulong)RETRY_LONG_SEC*1000;
      return;
   }
   PrintFormat("[IM] entry %s lots=%.2f dist=%.1f", side>0?"LONG":"SHORT", lots, dist);
   AnchorStopToFill(side, dist, spread);
}

void Evaluate(int k, datetime now)
{
   if(g_sigma[k]==EMPTY_VALUE) return;
   double p = iClose(_Symbol, PERIOD_M1, 1);
   if(p<=0) return;
   double aHi=MathMax(g_openPx,g_prevClose);
   double aLo=MathMin(g_openPx,g_prevClose);
   double ub=aHi*(1.0+g_sigma[k]);
   double lb=aLo*(1.0-g_sigma[k]);

   bool have=HasPosition();
   if(have)
   {
      long ptype=-1;
      for(int i=PositionsTotal()-1;i>=0;i--)
      {
         ulong t=PositionGetTicket(i);
         if(PositionGetString(POSITION_SYMBOL)==_Symbol && PositionGetInteger(POSITION_MAGIC)==InpMagic)
         { ptype=PositionGetInteger(POSITION_TYPE); break; }
      }
      if((ptype==POSITION_TYPE_BUY && p<ub) || (ptype==POSITION_TYPE_SELL && p>lb))
      { if(CloseMyPosition("stop banda semi-orario")) have=false; }
   }

   double dayPnl; int nLoss;
   DayStats(g_curDay, dayPnl, nLoss);
   if(dayPnl <= -EMERG_DAY_MULT*InpRiskDollars && HasPosition())
   { CloseMyPosition("emergenza perdita giornaliera"); return; }
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   // guardia extra su equity (comprende il flottante; validata mai attiva nel backtest)
   if(g_dayReady && eq <= AccountInfoDouble(ACCOUNT_BALANCE) - EMERG_DAY_MULT*InpRiskDollars && HasPosition())
   { CloseMyPosition("emergenza equity"); return; }
   bool blocked = (nLoss>=KILL_LOSSES || dayPnl<=-KILL_DAY_MULT*InpRiskDollars);
   if(blocked){ g_state="KILL-SWITCH GIORNO"; return; }
   if(g_dayGuardFired) return;
   if(PhaseTargetReached()) return;               // F5
   if(StrategyHalted()) return;

   if(!HasPosition())
   {
      if(p>ub)      TryEnter(+1,p,ub,now);
      else if(p<lb) TryEnter(-1,p,lb,now);
   }
}

//====================================================================
//  LOG TRADE (identico alla build A)
//====================================================================
void WriteTradeLog()
{
   if(!HistorySelect(0, TimeTradeServer()+60)) return;
   int nd=HistoryDealsTotal();
   int h=FileOpen(InpLogFileName, FILE_WRITE|FILE_CSV|FILE_ANSI, ';');
   if(h==INVALID_HANDLE) return;
   FileWrite(h,"position_id","dir","time_in","time_out","price_in","price_out","lots","net_pnl");
   long ids[]; int m=0; ArrayResize(ids,nd);
   for(int i=0;i<nd;i++)
   {
      ulong t=HistoryDealGetTicket(i);
      if(HistoryDealGetInteger(t,DEAL_MAGIC)!=InpMagic) continue;
      if(HistoryDealGetString(t,DEAL_SYMBOL)!=_Symbol) continue;
      long pid=HistoryDealGetInteger(t,DEAL_POSITION_ID);
      bool seen=false; for(int j=0;j<m;j++) if(ids[j]==pid){seen=true;break;}
      if(seen) continue;
      ids[m++]=pid;
      datetime ti=0,to=0; double pi=0,po=0,lots=0,net=0; int dir=0;
      for(int q=0;q<nd;q++)
      {
         ulong d=HistoryDealGetTicket(q);
         if(HistoryDealGetInteger(d,DEAL_POSITION_ID)!=pid) continue;
         long e=HistoryDealGetInteger(d,DEAL_ENTRY);
         net+=HistoryDealGetDouble(d,DEAL_PROFIT)+HistoryDealGetDouble(d,DEAL_COMMISSION)+HistoryDealGetDouble(d,DEAL_SWAP);
         if(e==DEAL_ENTRY_IN)
         { ti=(datetime)HistoryDealGetInteger(d,DEAL_TIME); pi=HistoryDealGetDouble(d,DEAL_PRICE);
           lots=HistoryDealGetDouble(d,DEAL_VOLUME);
           dir=(HistoryDealGetInteger(d,DEAL_TYPE)==DEAL_TYPE_BUY?1:-1); }
         if(e==DEAL_ENTRY_OUT || e==DEAL_ENTRY_OUT_BY)
         { to=(datetime)HistoryDealGetInteger(d,DEAL_TIME); po=HistoryDealGetDouble(d,DEAL_PRICE); }
      }
      if(to>0)
         FileWrite(h,(string)pid,(string)dir,TimeToString(ti,TIME_DATE|TIME_SECONDS),
                   TimeToString(to,TIME_DATE|TIME_SECONDS),
                   DoubleToString(pi,_Digits),DoubleToString(po,_Digits),
                   DoubleToString(lots,2),DoubleToString(net,2));
   }
   FileClose(h);
}

//====================================================================
//  PANNELLO DI STATO
//====================================================================
void UpdatePanel()
{
   double dayPnl; int nLoss;
   if(g_curDay>0) DayStats(g_curDay, dayPnl, nLoss); else { dayPnl=0; nLoss=0; }
   string news = !InpUseNewsFilter ? "spento" : (MQLInfoInteger(MQL_TESTER) ? "solo live" :
                 (g_calOk ? StringFormat("ATTIVO, bloccati oggi %d", g_newsBlocked) : "INATTIVO: calendario non disponibile"));
   string extra = StringFormat("\nNews: %s | richieste oggi %d/%d%s%s", news, g_reqCount, REQ_BUDGET_DAY,
                  g_closePending ? " | CHIUSURA IN ATTESA" : "",
                  g_duplicate ? "\n*** COPIA DUPLICATA: INATTIVA ***" : "");
   Comment(StringFormat("%s | %s\nStato: %s\nP&L oggi: %.0f$  perdite chiuse: %d\nRischio/trade: %.0f$  DST: %s%s",
           BUILD_ID, _Symbol, g_state, dayPnl, nLoss, InpRiskDollars,
           InpDSTMode==DST_US_ALIGNED?"US":"EU", extra));
}

//====================================================================
//  EVENT HANDLERS
//====================================================================
int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);
   long login = AccountInfoInteger(ACCOUNT_LOGIN);
   g_gvPeakEquity = StringFormat("IM_peak_%I64d_%d", login, (int)InpMagic);
   g_gvPhaseBase  = StringFormat("IM_base_%I64d_%d", login, (int)InpMagic);
   g_gvDayRef     = StringFormat("IMF_d0_%I64d_%d",   login, (int)InpMagic);
   g_gvDayRefDay  = StringFormat("IMF_d0d_%I64d_%d",  login, (int)InpMagic);
   g_gvGuardDay   = StringFormat("IMF_gd_%I64d_%d",   login, (int)InpMagic);
   g_gvReqCount   = StringFormat("IMF_rq_%I64d_%d",   login, (int)InpMagic);
   g_gvReqDay     = StringFormat("IMF_rqd_%I64d_%d",  login, (int)InpMagic);
   g_gvLockOwner  = StringFormat("IMF_lk_%I64d_%d",   login, (int)InpMagic);
   g_gvLockBeat   = StringFormat("IMF_lkb_%I64d_%d",  login, (int)InpMagic);
   EventSetTimer(15);
   MqlRates r[]; CopyRates(_Symbol, PERIOD_M1, 0, LOOKBACK_DAYS*3*1440, r);
   PrintFormat("[IM] init %s %s point=%g tickval=%.2f minlot=%.2f | verificare apertura cash sul server prima del live",
               BUILD_ID, _Symbol, _Point,
               SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_VALUE),
               SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN));
   if(AccountInfoString(ACCOUNT_CURRENCY)!="USD")
      Print("[IM] AVVISO: valuta conto != USD");
   if(!MQLInfoInteger(MQL_TESTER))
   {
      // BUILD F: rapporto di pre-volo, una volta all'avvio
      string why = "";
      bool okT = TradePermitted(false, why);
      PrintFormat("[IM] pre-volo: trading %s%s | budget richieste %d/giorno | terminale build %d",
                  okT ? "CONSENTITO" : "NON CONSENTITO: ", okT ? "" : why, REQ_BUDGET_DAY,
                  (int)TerminalInfoInteger(TERMINAL_BUILD));
      MqlDateTime st; TimeToStruct(TimeTradeServer(), st);
      if(InpUseNYSECalendar && st.year > CAL_LAST_YEAR)
         PrintFormat("[IM] *** ATTENZIONE: il calendario NYSE integrato arriva al %d: aggiornare l'EA per il %d. ***",
                     CAL_LAST_YEAR, st.year);
      CheckCalendar();
      LockInit();
      NoteTick();
      BudgetRoll();
   }
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason){ EventKillTimer(); Comment(""); WriteTradeLog(); LockRelease(); }

void OnTimer()
{
   datetime now = TimeTradeServer();                 // FIX2: avanza anche senza tick
   datetime day = DayStart(now);

   // BUILD F (D9): una sola copia attiva; (D1) ripresa della chiusura in attesa
   if(!MQLInfoInteger(MQL_TESTER))
   {
      LockBeat();
      BudgetRoll();
      if(g_duplicate){ UpdatePanel(); return; }
      if(g_closePending) CloseMyPosition(g_closeWhy);
   }

   // preparazione giornata anche senza tick (riavvii in giornate lente)
   if(day!=g_curDay && now >= day + SessOpenMinutes(day)*60)
   { g_curDay=day; PrepareDay(day); }

   // EOD forzata
   if(g_dayReady && !g_eodDone)
   {
      datetime eod = day + (g_sessOpenMinToday+FORCED_OFF)*60;
      if(now>=eod)
      {
         if(HasPosition()) CloseMyPosition("EOD 22:55");
         g_eodDone=true;
         WriteTradeLog();
      }
   }

   // GUARDIA EQUITY GIORNALIERA (build C): su timer, tra i check semi-orari.
   // BUILD G: soglia 4R (a R = 500$: 2.000$ come la build D; prima era min(9R, 2.000$) fissa).
   if(g_dayReady && !g_eodDone && !g_dayGuardFired)
   {
      double gEq = AccountInfoDouble(ACCOUNT_EQUITY);
      double thr = GUARD_R_MULT*InpRiskDollars;
      if(gEq <= g_dayStartEq - thr)
      {
         MarkGuardFired(g_curDay);                    // BUILD F (D2): persistente ai riavvii
         if(HasPosition()) CloseMyPosition("guardia equity giornaliera");
         g_state="GUARDIA EQUITY: giorno chiuso";
         PrintFormat("[IM] GUARDIA EQUITY: %.0f <= %.0f-%.0f — niente altri trade oggi", gEq, g_dayStartEq, thr);
      }
   }

   // FIX1 — rete di sicurezza riavvio-sicura:
   // chiudi SOLO se la posizione e' di un giorno precedente, oppure se e' di oggi
   // ma siamo oltre l'orario EOD. La posizione di oggi in orario si lascia correre.
   datetime posDay = MyPositionDay();
   if(posDay>0)
   {
      if(posDay < day)
         CloseMyPosition("posizione di un giorno precedente");
      else if(posDay==day && now >= day + (SessOpenMinutes(day)+FORCED_OFF)*60)
         CloseMyPosition("EOD recovery dopo riavvio");
      else if(!g_keepAliveLogged)
      { Print("[IM] posizione di oggi aperta: la gestisce l'EA (stop sul server, uscite ai check e alle 22:55)"); g_keepAliveLogged=true; }
   }
   UpdatePanel();
}

void OnTick()
{
   // BUILD F (D1): tick vivo -> mercato aperto; ripresa immediata della chiusura in attesa (es. 01:05)
   if(!MQLInfoInteger(MQL_TESTER))
   {
      NoteTick();
      if(g_duplicate) return;
      if(g_closePending) CloseMyPosition(g_closeWhy);
   }

   datetime bt = iTime(_Symbol, PERIOD_M1, 0);
   if(bt==g_lastM1Bar) return;
   g_lastM1Bar = bt;
   datetime day = DayStart(bt);

   if(day!=g_curDay)
   {
      int sm = SessOpenMinutes(day);
      if(bt >= day + sm*60){ g_curDay=day; PrepareDay(day); }
      else return;
   }
   else if(!g_dayReady && !g_daySkip)
      PrepareDay(day);
   if(!g_dayReady) return;

   long offMin = ((long)bt - ((long)g_curDay + (long)g_sessOpenMinToday*60))/60;
   if(offMin<SLOT_MIN || offMin>SLOT_MIN*N_CHECKS) return;
   if(offMin%SLOT_MIN!=0) return;
   int k=(int)(offMin/SLOT_MIN)-1;
   if(k<0||k>=N_CHECKS||g_checkDone[k]) return;
   g_checkDone[k]=true;
   Evaluate(k, bt);
}
//+------------------------------------------------------------------+
