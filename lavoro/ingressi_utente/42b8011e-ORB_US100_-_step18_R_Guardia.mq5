//+------------------------------------------------------------------+
//|                                            ORB_FTMO_EA_0715A.mq5 |
//|  [ORB BUILD 07-15-A]                                             |
//|                                                                  |
//|  CHANGELOG                                                       |
//|  10-09-R (09/10/2026) - GUARDIA RICHIESTE AL SERVER:             |
//|   copia della build Q2 (ORB_US100_-_step17_Q2.mq5, md5 375666b4).|
//|   Regola FTMO: max 2.000 richieste al giorno per conto (contano  |
//|   anche rifiuti e modifiche). La Q2 ritentava l'ingresso a ogni  |
//|   tick per 5 minuti e la chiusura EoD a ogni tick.               |
//|   - budget giornaliero di richieste in variabile globale         |
//|   - permessi e margine controllati in locale prima dell'ingresso |
//|   - max 3 invii d'ingresso al giorno, pausa 2 s, codici letti    |
//|   - ingresso in ritardo solo entro la deviation dal 1o segnale   |
//|   - chiusure fallite: pausa 10/60 s, max 30 tentativi al giorno  |
//|   InpGuardOn=false -> trading identico alla Q2 (regressione).    |
//|   Segnale, filtri, stop, TP, sizing, freni e orari: invariati.   |
//|   Design: DESIGN_GUARDIA_ORB_R_09-10-2026.md                     |
//|  07-15-A:                                                        |
//|   - ORARIO: ancorato al calendario USA (9:30 NY reali) con       |
//|     regole DST USA+EU. Niente TimeGMT (bugato nel tester).       |
//|     Sanity check sul volume della candela di apertura.           |
//|   - FILTRO GIORNATE: volume relativo (RVOL) + ampiezza           |
//|     candela 1 in % ATR (min/max). Entrambi ottimizzabili.        |
//|   - RISCHIO: dual-mode ($ fissi su baseline / % balance).        |
//|   - USCITE: parziale (trigger R e frazione regolabili) +         |
//|     breakeven con buffer dopo il parziale + trailing             |
//|     chandelier %ATR DISATTIVABILE (default OFF = corri a EoD).   |
//|   - NEWS: chiusura N min prima di FOMC/CPI/NFP/PCE da file CSV   |
//|     (Common\Files\ORB_news.csv, orari in ora NY).                |
//|   - GUARDIE: daily e total cap in $ FISSI sulla baseline.        |
//|   - OnTester: criterio personalizzato = Profitto / MaxDD equity  |
//|     (per ottimizzazione genetica orientata a FTMO).              |
//|  07-15-B (step1): OnTester = Profitto (DD soglia, min trade);    |
//|     calendario NYSE (skip giorni chiusi, mezze giornate 13:00);  |
//|  07-14-A: layer visuale. 07-13-A: prima versione.                |
//|                                                                  |
//|  07-27-H (build US100-only per evaluation FTMO):                |
//|   - DEFAULT: InpBufferPct 5.0 -> 6.5 (scelta Monte Carlo).      |
//|   - FIX pannello/log: la modalita' rischio veniva stampata      |
//|     sempre come "% balance" anche con RISK_BUFFER attivo.       |
//|     Ora mostra formula, floor, cap e rischio corrente in $.     |
//|   - CHIUSURA EoD VIA TIMER (OnTimer): indipendente dai tick,    |
//|     risolve il residuo del trade tenuto oltre la sessione nei   |
//|     pre-festivi. Disattivabile per regressione bit-identica.    |
//|   - DEVIATION in PUNTI INDICE (non in punti simbolo): non       |
//|     dipende piu' da digits/point del broker.                    |
//|   - MISURA SPREAD all'ingresso (media/peggiore) nel Diario.     |
//|   - MODALITA' OSSERVAZIONE: con Algo Trading spento o DryRun    |
//|     valuta il segnale e logga senza inviare ordini.             |
//|   - Avviso simbolo non NAS100/US100 e avviso se il rischio per  |
//|     trade si avvicina al freno giornaliero.                     |
//|                                                                  |
//|  NOTE: backtest SOLO "Ogni tick basato su tick reali".           |
//|  Slippage: non simulabile nei fill del tester; stress con        |
//|  "Ritardi" e post-analisi sulla lista trade.                     |
//+------------------------------------------------------------------+
#property copyright "Manu - ORB FTMO project"
#property version   "1.50"
#property description "5m ORB paper-1 - build US100-only per FTMO - BUILD 10-09-R (Q2 + guardia richieste al server)"

#include <Trade/Trade.mqh>

#define BUILD_ID   "ORB 10-09-R"
#define MAX_NEWS 400

//=== ENUM ===========================================================
enum ENUM_TIME_MODE
  {
   TIME_AUTO_NY = 0,   // Auto: ancorato a New York (consigliato)
   TIME_MANUAL  = 1    // Manuale: ora server fissa
  };
enum ENUM_SRV_TZ
  {
   SRV_EU_DST = 0,     // Server GMT+2/+3 con ora legale EU (FTMO/FPM)
   SRV_FIXED  = 1      // Server con offset GMT fisso
  };
enum ENUM_RISK_MODE
  {
   RISK_FIXED_USD = 0, // Dollari fissi sulla baseline (per FTMO)
   RISK_PCT_BAL   = 1, // Percentuale del balance (per compounding)
   RISK_BUFFER    = 2  // % del margine residuo sopra il floor (consigliato FTMO)
  };
enum ENUM_PFRAC
  {
   PFRAC_1_4 = 0,      // Chiudi 1/4
   PFRAC_1_3 = 1,      // Chiudi 1/3
   PFRAC_1_2 = 2       // Chiudi 1/2
  };
enum ENUM_CAL_MODE
  {
   CAL_AUTO = 0,       // Auto: rileva dal simbolo
   CAL_US   = 1,       // Forza calendario USA (NYSE)
   CAL_DE   = 2        // Forza calendario Germania (Xetra)
  };

//=== INPUT OPERATIVI ================================================
//    Solo cio' che va davvero toccato. Tutto il resto e' congelato piu'
//    sotto come costante: sono decisioni gia' validate fuori campione e
//    non devono poter essere cambiate per sbaglio dalla finestra del
//    tester o dalla scheda parametri.

//=== FILTRO DI ALLINEAMENTO (build Q) ===============================
// Unica differenza rispetto alla build P. Con InpAlignMode = FILTRO_OFF
// il comportamento e' identico bit per bit alla P: nessun ramo di codice
// nuovo viene attraversato. Serve per l'ancora di regressione.
enum ENUM_FILTRO_ALLIN
  {
   FILTRO_OFF      = 0,   // 0 = spento (identico alla build P)
   FILTRO_SINGOLO   = 1,   // 1 = riferimento singolo
   FILTRO_ENSEMBLE = 2    // 2 = ensemble a voti
  };

enum ENUM_RIF_ALLIN
  {
   RIF_EMA      = 0,     // 0 = media esponenziale
   RIF_SMA      = 1,     // 1 = media semplice
   RIF_CHIUSURA_N  = 2,     // 2 = chiusura di N barre fa
   RIF_META_RANGE = 3,     // 3 = meta' del range delle ultime N barre
   RIF_ROTTURA = 4      // 4 = rottura del range delle N barre precedenti
  };

input group "=== FILTRO DI ALLINEAMENTO (build Q) ==="
input ENUM_FILTRO_ALLIN InpAlignMode     = FILTRO_OFF; // Modalita': OFF = build P identica
input ENUM_RIF_ALLIN  InpAlignRef      = RIF_EMA;   // Riferimento (solo modalita' SINGOLO)
input int             InpAlignPeriod   = 12;        // Periodo del riferimento, in barre della candela 1
input double          InpAlignBufferR  = 0.15;      // Cuscinetto minimo dal riferimento, in multipli di R
input int             InpAlignMinVotes = 3;         // Voti minimi su 5 (solo modalita' ENSEMBLE)

input group "=== CONTO (adeguare alla taglia reale) ==="
input double InpFloorEquity     = 90000.0;    // Equity di fallimento FTMO (90% della taglia del conto)
input double InpBufferPct       = 5.0;        // Rischio = % del margine residuo sopra il floor
input double InpBufferCapUSD    = 1500.0;     // Rischio massimo per trade in USD (0 = nessun tetto)
input double InpAccountBaseline = 0;          // 0 = usa il balance al primo avvio (conto pulito)

input group "=== GUARDIE E TARGET DI FASE ==="
input double InpDailyLossCapUSD = 1500.0;     // Freno giornaliero in USD dalla equity di inizio giornata
input double InpTotalLossCapUSD = 8000.0;     // Freno totale in USD dalla baseline
input bool   InpUseProfitTarget = true;       // Ferma tutto quando la fase e' superata
input double InpProfitTargetUSD = 10000.0;    // Target sopra la baseline (fase 1 su 100k = 10000)
input double InpTargetBufferUSD = 0.0;        // >>> METTERE A 500 PRIMA DI OPERARE. 0 = ferma al tocco esatto

input group "=== ORARIO (dipende dal server del broker) ==="
input int    InpManualOpenHour   = 16;        // Ora di apertura del cash USA, ORA SERVER
input int    InpManualOpenMinute = 30;        // Minuto di apertura

input group "=== TAKE PROFIT (build K) ==="
input bool   InpUseTakeProfit  = true;        // true = TP a InpTPMultiple x R; false = comportamento build J (nessun TP)
input double InpTPMultiple     = 8.0;         // TP in multipli del rischio. Finestra validata 7-10R, ottimo in-sample 8R

input group "=== ESECUZIONE ==="
input long   InpMagic           = 20260715;   // Magic number
input double InpMaxSlipIndexPts = 5.0;        // Deviation massima in PUNTI INDICE
input bool   InpDryRun          = false;      // true = OSSERVAZIONE: valuta e logga il segnale senza inviare ordini
input bool   InpDrawObjects     = false;      // Disegna livelli e marker (utile solo su grafico in demo)

input group "=== GUARDIA RICHIESTE AL SERVER (build R) ==="
input bool   InpGuardOn          = true;      // Guardia attiva. false = trading identico alla build Q2 (solo per la regressione)
input int    InpGuardDailyBudget = 100;       // Richieste massime al server al giorno per questo EA (FTMO: 2000 per l'intero conto)

//=== PARAMETRI CONGELATI ============================================
//    Non sono input di proposito. Ogni valore qui sotto e' l'esito di
//    una validazione fuori campione gia' fatta; riaprirli richiede un
//    motivo nuovo e forte, non una riga cambiata al volo.
//
//    Strategia   : Paper 1 Zarattini & Aziz, prima candela M5 della
//                  sessione cash USA, ingresso all'apertura della
//                  candela 2, stop 10% ATR(14) daily, TP a InpTPMultiple*R (build K),
//                  chiusura a fine sessione, un solo trade al giorno.
//    Bocciati    : RVOL (il tick volume dei CFD non discrimina), tetto
//                  di ampiezza, presa di profitto parziale, breakeven,
//                  trailing, VWAP, filtro news. Tutti testati, tutti
//                  peggiorativi o inutilizzabili. Le costanti restano
//                  perche' il codice le legge; i rami sono spenti.

//--- orario e calendario
const ENUM_TIME_MODE   InpTimeMode           = TIME_MANUAL;   // AUTO_NY sbagliato: il server segue la DST USA
const ENUM_SRV_TZ      InpServerTZ           = SRV_EU_DST;
const int              InpServerBaseGMT      = 2;
const int              InpSessionMinutes     = 390;           // durata sessione cash USA
const int              InpMinutesBeforeClose = 5;             // chiusura EoD 5 minuti prima
const ENUM_CAL_MODE    InpCalendar           = CAL_AUTO;      // -> NYSE dal simbolo

//--- strategia base
const ENUM_TIMEFRAMES  InpORTimeframe        = PERIOD_M5;
const int              InpATRPeriod          = 14;
const double           InpStopATRPct         = 10.0;          // altopiano 10-13%, il 5% del paper non si trasferisce
const double           InpMinBodyPctRange    = 5.0;           // doji: salta se body < 5% del range
const bool             InpAllowLong          = true;
const bool             InpAllowShort         = true;

//--- filtro giornate
const bool             InpUseRangeGate       = true;
const double           InpRangeMinPctATR     = 12.0;          // unica soglia positiva in tutti i sotto-periodi
const double           InpRangeMaxPctATR     = 999.0;         // tetto DISATTIVATO: era dannoso
const bool             InpUseRVOL            = false;         // inutilizzabile sui CFD
const double           InpRVOLThreshold      = 1.0;
const int              InpRVOLLookback       = 14;

//--- rischio
//    ESPOSTI COME input DALLA BUILD O, default INVARIATI: servono solo al
//    conto combinato con la strategia intraday momentum. L'ORB da solo resta
//    su RISK_BUFFER 5% (decisione chiusa: il buffer rende il floor FTMO
//    irraggiungibile per costruzione, il rischio fisso no).
input ENUM_RISK_MODE   InpRiskMode           = RISK_BUFFER;   // Modalita' rischio (BUFFER = ORB da solo)
input double           InpRiskFixedUSD       = 300.0;         // Rischio $ fisso (solo se modalita' = dollari fissi)
const double           InpRiskPct            = 0.3;
const double           InpMaxRiskOvershoot   = 1.3;           // skip se il lotto minimo rischia > target*X

//--- uscite: tutte bocciate su MFE/MAE ricostruiti al minuto
const bool             InpUsePartial         = false;
const double           InpPartialTriggerR    = 1.0;
const ENUM_PFRAC       InpPartialFrac        = PFRAC_1_3;
const double           InpBEBufferPoints     = 2.0;
const bool             InpUseTrailing        = false;
const double           InpTrailATRPct        = 35.0;

//--- filtro news: mai testato, serve solo per altri prop firm
const bool             InpUseNews            = false;
const int              InpNewsCloseMinBefore = 5;
const string           InpNewsCSVName        = "ORB_news.csv";

//--- precisione e sicurezza
const bool             InpAnchorSLToFill     = true;          // riallinea lo stop al prezzo ESEGUITO
const bool             InpUseEoDTimer        = true;          // chiusura EoD anche senza tick
const int              InpEoDTimerSec        = 10;
const bool             InpCleanChartOnExit   = false;

//--- guardia richieste al server (build R): congelati come il resto.
//    Design: DESIGN_GUARDIA_ORB_R_09-10-2026.md (G1-G8). L'inseguimento
//    massimo di un ingresso in ritardo e' InpMaxSlipIndexPts (deviation).
const int              GUARD_MAX_ENTRY_SENDS      = 3;      // invii d'ingresso al giorno
const int              GUARD_RETRY_PAUSE_SEC      = 2;      // pausa minima fra due invii d'ingresso
const double           GUARD_MARGIN_SAFETY        = 1.00;   // invio solo se margine richiesto <= libero x questo
const int              GUARD_CLOSE_PAUSE_SEC      = 10;     // pausa dopo una chiusura rifiutata
const int              GUARD_CLOSE_PAUSE_PERM_SEC = 60;     // pausa dopo un rifiuto permanente
const int              GUARD_MAX_CLOSE_SENDS      = 30;     // tentativi di chiusura al giorno

//=== CALENDARIO BORSA USA (fonte: NYSE). Aggiornare 1 volta l'anno. ==
string g_us_closed =
  "2019.01.01,2019.01.21,2019.02.18,2019.04.19,2019.05.27,2019.07.04,2019.09.02,2019.11.28,2019.12.25,"
  "2020.01.01,2020.01.20,2020.02.17,2020.04.10,2020.05.25,2020.07.03,2020.09.07,2020.11.26,2020.12.25,"
  "2021.01.01,2021.01.18,2021.02.15,2021.04.02,2021.05.31,2021.07.05,2021.09.06,2021.11.25,2021.12.24,"
  "2022.01.17,2022.02.21,2022.04.15,2022.05.30,2022.06.20,2022.07.04,2022.09.05,2022.11.24,2022.12.26,"
  "2023.01.02,2023.01.16,2023.02.20,2023.04.07,2023.05.29,2023.06.19,2023.07.04,2023.09.04,2023.11.23,2023.12.25,"
  "2024.01.01,2024.01.15,2024.02.19,2024.03.29,2024.05.27,2024.06.19,2024.07.04,2024.09.02,2024.11.28,2024.12.25,"
  "2025.01.01,2025.01.09,2025.01.20,2025.02.17,2025.04.18,2025.05.26,2025.06.19,2025.07.04,2025.09.01,2025.11.27,2025.12.25,"
  "2026.01.01,2026.01.19,2026.02.16,2026.04.03,2026.05.25,2026.06.19,2026.07.03,2026.09.07,2026.11.26,2026.12.25,"
  "2027.01.01,2027.01.18,2027.02.15,2027.03.26,2027.05.31,2027.06.18,2027.07.05,2027.09.06,2027.11.25,2027.12.24,";

string g_us_half =   // mezze giornate: chiusura 13:00 ET
  "2019.07.03,2019.11.29,2019.12.24,2020.11.27,2020.12.24,2021.11.26,2022.11.25,"
  "2023.07.03,2023.11.24,2024.07.03,2024.11.29,2024.12.24,2025.07.03,2025.11.28,2025.12.24,"
  "2026.11.27,2026.12.24,2027.07.02,2027.11.26,2027.12.23,";

bool DateInList(const string &list, datetime nyTime)
  {
   MqlDateTime s; TimeToStruct(nyTime, s);
   string key = StringFormat("%04d.%02d.%02d", s.year, s.mon, s.day);
   return (StringFind(list, key) >= 0);
  }

//=== CALENDARIO BORSA TEDESCA (FWB/Xetra, fonte: Deutsche Boerse) ====
// Chiusure: 1/1, Ven.Santo, Lun.Angelo, 1/5, 24-25-26/12, 31/12.
// Pentecoste: chiusa fino al 2024, GIORNO DI TRADING dal 2025.
// 3 ottobre (Unita' tedesca): Xetra APERTA -> non filtrato.
// Nessuna mezza giornata su Xetra.
string g_de_closed =
  "2019.01.01,2019.04.19,2019.04.22,2019.05.01,2019.06.10,2019.12.24,2019.12.25,2019.12.26,2019.12.31,"
  "2020.01.01,2020.04.10,2020.04.13,2020.05.01,2020.06.01,2020.12.24,2020.12.25,2020.12.26,2020.12.31,"
  "2021.01.01,2021.04.02,2021.04.05,2021.05.01,2021.05.24,2021.12.24,2021.12.25,2021.12.26,2021.12.31,"
  "2022.01.01,2022.04.15,2022.04.18,2022.05.01,2022.06.06,2022.12.24,2022.12.25,2022.12.26,2022.12.31,"
  "2023.01.01,2023.04.07,2023.04.10,2023.05.01,2023.05.29,2023.12.24,2023.12.25,2023.12.26,2023.12.31,"
  "2024.01.01,2024.03.29,2024.04.01,2024.05.01,2024.05.20,2024.12.24,2024.12.25,2024.12.26,2024.12.31,"
  "2025.01.01,2025.04.18,2025.04.21,2025.05.01,2025.12.24,2025.12.25,2025.12.26,2025.12.31,"
  "2026.01.01,2026.04.03,2026.04.06,2026.05.01,2026.12.24,2026.12.25,2026.12.26,2026.12.31,"
  "2027.01.01,2027.03.26,2027.03.29,2027.05.01,2027.12.24,2027.12.25,2027.12.26,2027.12.31,";

bool IsGermanSymbol()
  {
   string s=_Symbol;
   StringToUpper(s);
   return (StringFind(s,"GER")>=0 || StringFind(s,"DE40")>=0 ||
           StringFind(s,"DE30")>=0 || StringFind(s,"DAX")>=0);
  }

bool CalendarIsDE()
  {
   if(InpCalendar==CAL_DE) return(true);
   if(InpCalendar==CAL_US) return(false);
   return(IsGermanSymbol());
  }

// NB: niente operatore ternario nell'argomento -> MQL5 richiede una
// variabile vera per un parametro passato per riferimento.
bool MarketClosedToday(datetime t)
  {
   if(CalendarIsDE())
      return(DateInList(g_de_closed, t));
   return(DateInList(g_us_closed, t));
  }

bool HalfDayToday(datetime t)
  {
   if(CalendarIsDE()) return(false);      // Xetra: nessuna mezza giornata
   return(DateInList(g_us_half, t));
  }

//=== STATO GLOBALE ==================================================
CTrade    g_trade;
int       g_hATR          = INVALID_HANDLE;
int       g_hAlignEMA     = INVALID_HANDLE;   // build Q
int       g_hAlignSMA     = INVALID_HANDLE;   // build Q
double    g_alignGapR     = 0.0;              // build Q: scarto misurato oggi, in R
int       g_alignVotes    = -1;               // build Q: voti dell'ensemble oggi
int       g_lastDayId     = -1;
datetime  g_sessOpen      = 0;
datetime  g_sessCloseCut  = 0;
datetime  g_entryDeadline = 0;
double    g_dailyRefEq    = 0;
double    g_baseline      = 0;
bool      g_dailyBlocked  = false;
bool      g_totalBlocked  = false;
bool      g_targetReached  = false;   // target di fase raggiunto: stop ai nuovi trade
bool      g_doneToday     = false;
string    g_lastReason    = "init";
double    g_rvolToday     = -1;

//--- tracking posizione / uscite
bool      g_trackOpen     = false;
bool      g_trackLong     = false;
double    g_trackEntry    = 0;
double    g_trackSL       = 0;      // SL iniziale
double    g_curSL         = 0;      // SL corrente (dopo BE/trailing)
double    g_trackRdist    = 0;
datetime  g_trackTime     = 0;
bool      g_partialDone   = false;
bool      g_beDone        = false;
double    g_hh            = 0;
double    g_ll            = 0;
datetime  g_lastBarTime   = 0;
bool      g_selfClosing   = false;

//--- tracking metriche FTMO (solo misura, non tocca la logica di trading)
double    g_initEq        = 0;   // equity all'avvio del test
double    g_peakEq        = 0;   // massimo equity raggiunto
double    g_minEq         = 0;   // minimo equity raggiunto
double    g_maxRelDDpct   = 0;   // max drawdown picco-minimo (%)
double    g_maxDayLoss    = 0;   // max perdita in una singola giornata (USD)
double    g_slipSum       = 0;   // somma slippage d'ingresso (punti prezzo, +=sfavorevole)
double    g_slipMax       = 0;   // slippage d'ingresso peggiore
int       g_slipN         = 0;   // numero di ingressi misurati

//--- news
datetime  g_news[MAX_NEWS];
int       g_newsCount     = 0;

//--- visual
bool      g_canDraw       = false;
bool      g_c1Drawn       = false;

//--- esecuzione e misure di mercato (build H)
int       g_devPoints     = 0;   // deviation in punti simbolo, calcolata in OnInit
double    g_sprSum        = 0;   // somma spread misurato all'ingresso (punti indice)
double    g_sprMax        = 0;   // spread peggiore all'ingresso
int       g_sprN          = 0;   // numero di misure di spread
int       g_eodTries      = 0;   // tentativi di chiusura EoD del timer (azzerati ogni giorno)

//--- guardia richieste al server (build R)
string    g_gvReq          = "";      // variabile globale: richieste di oggi
string    g_gvReqDay       = "";      // variabile globale: data (AAAAMMGG) del contatore
int       g_gReqToday      = 0;       // richieste di oggi (copia in memoria)
int       g_gEntrySends    = 0;       // invii d'ingresso di oggi
int       g_gCloseSends    = 0;       // tentativi di chiusura di oggi
int       g_gCloseFails    = 0;       // chiusure rifiutate oggi
datetime  g_gLastEntrySend = 0;       // ora dell'ultimo invio d'ingresso
datetime  g_gNextCloseOK   = 0;       // prima ora utile per ritentare una chiusura rifiutata
datetime  g_gLastRecheck   = 0;       // ultimo ricontrollo del segnale in attesa (1 al secondo)
double    g_gFirstPrice    = 0.0;     // prezzo del primo segnale valido di oggi (0 = nessuno)
bool      g_gMarginWait    = false;   // in attesa che il margine si liberi
bool      g_gSignalLogged  = false;   // righe del segnale gia' stampate oggi
bool      g_gBudgetLogged  = false;   // avviso di budget esaurito gia' stampato oggi
bool      g_gCloseCapLogged= false;   // avviso di tetto chiusure gia' stampato oggi
int       g_gLastRetcode   = 0;       // codice dell'ultimo rifiuto
string    g_gReason        = "";      // ultima azione della guardia (pannello)

//=== UTILITY TEMPO ==================================================
datetime MakeDT(int y, int m, int d, int h, int mi)
  {
   MqlDateTime s;
   ZeroMemory(s);
   s.year=y; s.mon=m; s.day=d; s.hour=h; s.min=mi; s.sec=0;
   return StructToTime(s);
  }

int DayOfWeekOf(datetime t)
  {
   MqlDateTime s;
   TimeToStruct(t, s);
   return s.day_of_week; // 0=domenica
  }

// DST USA: dalla 2a domenica di marzo alla 1a domenica di novembre
bool IsUSDST(int y, int m, int d)
  {
   if(m>3 && m<11) return true;
   if(m<3 || m>11) return false;
   if(m==3)
     {
      int dow1 = DayOfWeekOf(MakeDT(y,3,1,0,0));
      int secondSun = 1 + ((7-dow1)%7) + 7;
      return (d >= secondSun);
     }
   int dowN = DayOfWeekOf(MakeDT(y,11,1,0,0));
   int firstSun = 1 + ((7-dowN)%7);
   return (d < firstSun);
  }

// DST EU: dall'ultima domenica di marzo all'ultima domenica di ottobre
bool IsEUDST(int y, int m, int d)
  {
   if(m>3 && m<10) return true;
   if(m<3 || m>10) return false;
   int dowLast = DayOfWeekOf(MakeDT(y,m,31,0,0));
   int lastSun = 31 - dowLast;
   if(m==3) return (d >= lastSun);
   return (d < lastSun); // ottobre
  }

int ServerGMTOffset(int y, int m, int d)
  {
   int off = InpServerBaseGMT;
   if(InpServerTZ==SRV_EU_DST && IsEUDST(y,m,d)) off++;
   return off;
  }

int NYGMTOffset(int y, int m, int d)
  {
   return IsUSDST(y,m,d) ? -4 : -5;
  }

// Apertura sessione (9:30 NY) in ora server, per la data del timestamp passato
datetime SessionOpenForDate(datetime anyTimeThatDay)
  {
   MqlDateTime s;
   TimeToStruct(anyTimeThatDay, s);
   if(InpTimeMode==TIME_MANUAL)
      return MakeDT(s.year, s.mon, s.day, InpManualOpenHour, InpManualOpenMinute);
   int hSrv = 9 + (ServerGMTOffset(s.year,s.mon,s.day) - NYGMTOffset(s.year,s.mon,s.day));
   return MakeDT(s.year, s.mon, s.day, hSrv, 30);
  }

// Converte un orario NY (per una data) in ora server
datetime NYToServer(int y, int m, int d, int h, int mi)
  {
   int hSrv = h + (ServerGMTOffset(y,m,d) - NYGMTOffset(y,m,d));
   return MakeDT(y, m, d, hSrv, mi);
  }

//=== UTILITY VARIE ==================================================
double DailyATR()
  {
   double buf[1];
   if(CopyBuffer(g_hATR, 0, 1, 1, buf)!=1) return 0.0;
   return buf[0];
  }

double NormPrice(double p)
  {
   double ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(ts>0) p = MathRound(p/ts)*ts;
   return NormalizeDouble(p, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS));
  }

double NormVol(double v)
  {
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   if(step<=0) step=0.01;
   v = MathFloor(v/step)*step;
   int dg=0; double s=step;
   while(s<1.0 && dg<8){ s*=10.0; dg++; }
   return NormalizeDouble(v, dg);
  }

bool GetMyPosition(ulong &ticket, double &vol, long &ptype, double &popen, double &psl)
  {
   for(int i=PositionsTotal()-1; i>=0; i--)
     {
      ulong tk = PositionGetTicket(i);
      if(tk==0) continue;
      if(PositionGetString(POSITION_SYMBOL)==_Symbol &&
         PositionGetInteger(POSITION_MAGIC)==InpMagic)
        {
         ticket=tk;
         vol   = PositionGetDouble(POSITION_VOLUME);
         ptype = PositionGetInteger(POSITION_TYPE);
         popen = PositionGetDouble(POSITION_PRICE_OPEN);
         psl   = PositionGetDouble(POSITION_SL);
         return true;
        }
     }
   return false;
  }

bool HasPosition()
  {
   ulong tk; double v; long ty; double po,ps;
   return GetMyPosition(tk,v,ty,po,ps);
  }

// Giorno (AAAAMMGG, ora server) in cui e' stata aperta la NOSTRA posizione.
// Ritorna -1 se non c'e' posizione. Serve al catch-all di OnNewDay per
// distinguere una posizione rimasta aperta da un giorno precedente (va
// chiusa) da una aperta oggi (va lasciata correre). Necessario perche'
// g_lastDayId, come ogni variabile globale, si azzera a -1 a OGNI
// reinizializzazione dell'EA: senza questo controllo un semplice riavvio
// del terminale chiude la posizione del giorno in corso.
int MyPositionDayId()
  {
   for(int i=PositionsTotal()-1; i>=0; i--)
     {
      ulong tk = PositionGetTicket(i);
      if(tk==0) continue;
      if(PositionGetString(POSITION_SYMBOL)==_Symbol &&
         PositionGetInteger(POSITION_MAGIC)==InpMagic)
        {
         datetime pt = (datetime)PositionGetInteger(POSITION_TIME);
         MqlDateTime s;
         TimeToStruct(pt, s);
         return(s.year*10000 + s.mon*100 + s.day);
        }
     }
   return(-1);
  }

//=== MISURE DI MERCATO ==============================================
// Spread in PUNTI INDICE (differenza di prezzo): confrontabile fra
// broker diversi, a differenza dei punti simbolo.
double SpreadIndexPts()
  {
   double a=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
   double b=SymbolInfoDouble(_Symbol,SYMBOL_BID);
   if(a<=0 || b<=0) return(-1.0);
   return(a-b);
  }

bool TradingIsLive()
  {
   if(InpDryRun) return(false);
   if(MQLInfoInteger(MQL_TRADE_ALLOWED)==0)         return(false);
   if(AccountInfoInteger(ACCOUNT_TRADE_EXPERT)==0)  return(false);
   return(true);
  }

//=== GUARDIA RICHIESTE AL SERVER (build R) ==========================
// Regola FTMO: al massimo 2.000 richieste al server al giorno per conto;
// contano anche gli ordini rifiutati e le modifiche. La Q2 ritentava
// l'ingresso a ogni tick per 5 minuti (25/09/2026: ~3.000 richieste) e la
// chiusura di fine giornata a ogni tick. Qui ogni richiesta passa da un
// contatore con budget giornaliero; permessi e margine si controllano in
// locale (nessuna richiesta) prima dell'ingresso. Con InpGuardOn=false
// nessuna funzione interviene: il trading e' identico alla Q2.
// Design: DESIGN_GUARDIA_ORB_R_09-10-2026.md (G1-G8).

// Ora server che avanza anche senza tick (come in OnTimer). Nel tester
// solo l'ora simulata: il budget giornaliero deve seguire i giorni del test.
datetime GuardNow()
  {
   if(MQLInfoInteger(MQL_TESTER)) return(TimeCurrent());
   datetime a = TimeTradeServer();
   datetime b = TimeCurrent();
   return(a>b ? a : b);
  }

int GuardDayKey()
  {
   MqlDateTime s;
   TimeToStruct(GuardNow(), s);
   return(s.year*10000 + s.mon*100 + s.day);
  }

//--- G1: il contatore vive in una variabile globale del terminale, cosi'
//    sopravvive a un riavvio; al cambio di data si azzera.
void GuardSyncDay()
  {
   if(g_gvReq=="" || g_gvReqDay=="") return;
   int key = GuardDayKey();
   if(!GlobalVariableCheck(g_gvReq) || !GlobalVariableCheck(g_gvReqDay) ||
      (int)GlobalVariableGet(g_gvReqDay)!=key)
     {
      GlobalVariableSet(g_gvReqDay, (double)key);
      GlobalVariableSet(g_gvReq, 0.0);
      g_gBudgetLogged = false;
     }
   g_gReqToday = (int)GlobalVariableGet(g_gvReq);
  }

//--- G1: true = la richiesta si puo' inviare (budget di oggi non esaurito)
bool GuardCanSend(string what)
  {
   if(!InpGuardOn) return(true);
   GuardSyncDay();
   if(g_gReqToday < InpGuardDailyBudget) return(true);
   if(!g_gBudgetLogged)
     {
      PrintFormat("[ORB][GUARDIA] *** BUDGET ESAURITO: %d richieste oggi (massimo %d). %s non inviata: nessuna altra richiesta fino a domani. SL e TP restano sul server. ***",
                  g_gReqToday, InpGuardDailyBudget, what);
      g_gBudgetLogged = true;
     }
   g_gReason = "budget esaurito";
   return(false);
  }

//--- G1: da chiamare subito dopo ogni richiesta effettivamente inviata
void GuardAfterSend(bool ok)
  {
   if(!InpGuardOn) return;
   GuardSyncDay();
   g_gReqToday++;
   if(g_gvReq!="") GlobalVariableSet(g_gvReq, (double)g_gReqToday);
   if(!ok) g_gLastRetcode = (int)g_trade.ResultRetcode();
  }

//--- G4: rifiuti per cui ha senso ritentare l'ingresso (dentro il tetto).
//    Ogni altro codice chiude i tentativi del giorno.
bool GuardRetryable(uint rc)
  {
   return(rc==TRADE_RETCODE_REQUOTE       || rc==TRADE_RETCODE_REJECT    ||
          rc==TRADE_RETCODE_ERROR         || rc==TRADE_RETCODE_TIMEOUT   ||
          rc==TRADE_RETCODE_PRICE_CHANGED || rc==TRADE_RETCODE_PRICE_OFF ||
          rc==TRADE_RETCODE_CONNECTION);
  }

//--- G6: rifiuti che non si risolvono a breve: pausa lunga fra le chiusure
bool GuardPermanent(uint rc)
  {
   return(rc==TRADE_RETCODE_TRADE_DISABLED     || rc==TRADE_RETCODE_MARKET_CLOSED     ||
          rc==TRADE_RETCODE_SERVER_DISABLES_AT || rc==TRADE_RETCODE_CLIENT_DISABLES_AT ||
          rc==TRADE_RETCODE_CLOSE_ONLY);
  }

string GuardRetcodeText(uint rc)
  {
   switch((int)rc)
     {
      case TRADE_RETCODE_REQUOTE:            return("requote");
      case TRADE_RETCODE_REJECT:             return("richiesta rifiutata");
      case TRADE_RETCODE_ERROR:              return("errore di elaborazione");
      case TRADE_RETCODE_TIMEOUT:            return("timeout");
      case TRADE_RETCODE_INVALID:            return("richiesta non valida");
      case TRADE_RETCODE_INVALID_VOLUME:     return("volume non valido");
      case TRADE_RETCODE_INVALID_PRICE:      return("prezzo non valido");
      case TRADE_RETCODE_INVALID_STOPS:      return("stop non validi");
      case TRADE_RETCODE_TRADE_DISABLED:     return("trading disabilitato");
      case TRADE_RETCODE_MARKET_CLOSED:      return("mercato chiuso");
      case TRADE_RETCODE_NO_MONEY:           return("margine insufficiente");
      case TRADE_RETCODE_PRICE_CHANGED:      return("prezzo cambiato");
      case TRADE_RETCODE_PRICE_OFF:          return("nessuna quotazione");
      case TRADE_RETCODE_TOO_MANY_REQUESTS:  return("troppe richieste");
      case TRADE_RETCODE_SERVER_DISABLES_AT: return("Algo Trading disabilitato dal server");
      case TRADE_RETCODE_CLIENT_DISABLES_AT: return("Algo Trading disabilitato nel terminale");
      case TRADE_RETCODE_CONNECTION:         return("nessuna connessione");
      case TRADE_RETCODE_LIMIT_VOLUME:       return("limite di volume");
      case TRADE_RETCODE_LIMIT_POSITIONS:    return("limite di posizioni");
      case TRADE_RETCODE_CLOSE_ONLY:         return("solo chiusure consentite");
     }
   return("altro codice");
  }

//--- azzeramento giornaliero (chiamato a inizio OnNewDay e in OnInit)
void GuardNewDay()
  {
   g_gEntrySends     = 0;
   g_gCloseSends     = 0;
   g_gCloseFails     = 0;
   g_gLastEntrySend  = 0;
   g_gNextCloseOK    = 0;
   g_gLastRecheck    = 0;
   g_gFirstPrice     = 0.0;
   g_gMarginWait     = false;
   g_gSignalLogged   = false;
   g_gCloseCapLogged = false;
   g_gLastRetcode    = 0;
   g_gReason         = "";
   if(InpGuardOn) GuardSyncDay();
  }

//--- la guardia chiude i tentativi d'ingresso di oggi
void GuardCloseDay(string why)
  {
   g_doneToday  = true;
   g_gReason    = why;
   g_lastReason = "skip: guardia";
   PrintFormat("[ORB][GUARDIA] SKIP: %s. Giorno concluso senza altri invii (richieste oggi %d/%d).",
               why, g_gReqToday, InpGuardDailyBudget);
  }

//--- G2: permessi di trading (controllo locale, nessuna richiesta)
bool GuardTradeAllowed(bool goLong, string &why)
  {
   why = "";
   if(!MQLInfoInteger(MQL_TESTER) && TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)==0)
     {
      why = "Algo Trading spento nel terminale";
      return(false);
     }
   if(AccountInfoInteger(ACCOUNT_TRADE_ALLOWED)==0)
     {
      why = "trading disabilitato sul conto";
      return(false);
     }
   long mode = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE);
   if(mode==SYMBOL_TRADE_MODE_FULL)                  return(true);
   if(goLong  && mode==SYMBOL_TRADE_MODE_LONGONLY)   return(true);
   if(!goLong && mode==SYMBOL_TRADE_MODE_SHORTONLY)  return(true);
   why = StringFormat("simbolo non negoziabile in questa direzione (modo %d)", (int)mode);
   return(false);
  }

//--- G3: margine (controllo locale). true = il margine libero basta.
//    Il server rifiuta se il margine richiesto supera il libero (misurato
//    il 07/10/2026 sul Free Trial Swing: 50 lotti rifiutati "No money",
//    45 accettati); qui si applica la stessa regola senza mandare nulla.
//    Se il calcolo non e' disponibile decide il server (dentro il tetto G4).
bool GuardMarginOK(bool goLong, double lots, double price, double &need, double &freeM)
  {
   need  = 0.0;
   freeM = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
   if(!OrderCalcMargin(goLong ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, _Symbol, lots, price, need))
      return(true);
   return(need <= freeM*GUARD_MARGIN_SAFETY);
  }

//--- G2-G5 prima di ogni invio d'ingresso. false = non inviare adesso:
//    o il giorno e' concluso (GuardCloseDay), o si attende (pausa fra due
//    invii, margine che si libera) senza mandare nessuna richiesta.
bool GuardPreEntry(bool goLong, double lots, double entry)
  {
   string why;
   //--- G2: permessi
   if(!GuardTradeAllowed(goLong, why))
     {
      GuardCloseDay("trading non consentito: " + why);
      return(false);
     }
   //--- G4: tetto agli invii e pausa fra un invio e l'altro
   if(g_gEntrySends >= GUARD_MAX_ENTRY_SENDS)
     {
      GuardCloseDay(StringFormat("%d invii d'ingresso gia' fatti oggi", g_gEntrySends));
      return(false);
     }
   if(g_gEntrySends > 0 && GuardNow() < g_gLastEntrySend + GUARD_RETRY_PAUSE_SEC)
      return(false);
   //--- G5: un ingresso in ritardo solo entro la deviation dal primo segnale
   if(g_gFirstPrice <= 0.0)
      g_gFirstPrice = entry;
   else if(MathAbs(entry - g_gFirstPrice) > InpMaxSlipIndexPts)
     {
      GuardCloseDay(StringFormat("prezzo %.2f a %.2f punti dal primo segnale (%.2f), oltre la deviation di %.2f",
                                 entry, MathAbs(entry - g_gFirstPrice), g_gFirstPrice, InpMaxSlipIndexPts));
      return(false);
     }
   //--- G3: margine
   double need, freeM;
   if(!GuardMarginOK(goLong, lots, entry, need, freeM))
     {
      if(!g_gMarginWait)
        {
         PrintFormat("[ORB][GUARDIA] Margine insufficiente: richiesto %.2f, libero %.2f per %.2f lotti. Nessun ordine: ricontrollo in locale fino alle %s.",
                     need, freeM, lots, TimeToString(g_entryDeadline, TIME_MINUTES));
         g_gMarginWait = true;
         g_gReason     = "attesa margine";
        }
      return(false);
     }
   if(g_gMarginWait)
     {
      PrintFormat("[ORB][GUARDIA] Margine ora sufficiente: richiesto %.2f, libero %.2f. Invio.", need, freeM);
      g_gMarginWait = false;
      g_gReason     = "";
     }
   return(true);
  }

//--- G4: dopo un ingresso rifiutato
void GuardEntryFailed(uint rc)
  {
   if(GuardRetryable(rc) && g_gEntrySends < GUARD_MAX_ENTRY_SENDS)
     {
      g_gReason = StringFormat("ingresso rifiutato %u, ritento", rc);
      PrintFormat("[ORB][GUARDIA] Ingresso rifiutato (retcode %u = %s): nuovo invio fra almeno %d s (invii oggi %d di %d).",
                  rc, GuardRetcodeText(rc), GUARD_RETRY_PAUSE_SEC, g_gEntrySends, GUARD_MAX_ENTRY_SENDS);
      return;
     }
   GuardCloseDay(StringFormat("ingresso rifiutato (retcode %u = %s), invii oggi %d di %d",
                              rc, GuardRetcodeText(rc), g_gEntrySends, GUARD_MAX_ENTRY_SENDS));
  }

//--- G6: true = si puo' tentare una chiusura adesso
bool GuardCanClose()
  {
   if(!InpGuardOn) return(true);
   if(GuardNow() < g_gNextCloseOK) return(false);      // pausa dopo un rifiuto: nessuna richiesta
   if(g_gCloseSends >= GUARD_MAX_CLOSE_SENDS)
     {
      if(!g_gCloseCapLogged)
        {
         PrintFormat("[ORB][GUARDIA] *** %d tentativi di chiusura oggi: nessun altro tentativo fino a domani. La posizione resta protetta da SL e TP sul server. ***",
                     g_gCloseSends);
         g_gCloseCapLogged = true;
        }
      return(false);
     }
   return(GuardCanSend("chiusura"));
  }

//--- G6: dopo ogni tentativo di chiusura
void GuardAfterClose(bool ok)
  {
   if(!InpGuardOn) return;
   g_gCloseSends++;
   GuardAfterSend(ok);
   if(ok) return;
   uint rc = g_trade.ResultRetcode();
   g_gCloseFails++;
   int pausa = (GuardPermanent(rc) ? GUARD_CLOSE_PAUSE_PERM_SEC : GUARD_CLOSE_PAUSE_SEC);
   g_gNextCloseOK = GuardNow() + pausa;
   g_gReason = StringFormat("chiusura rifiutata %u", rc);
   PrintFormat("[ORB][GUARDIA] Chiusura rifiutata (retcode %u = %s): prossimo tentativo fra %d s (tentativi oggi %d di %d).",
               rc, GuardRetcodeText(rc), pausa, g_gCloseSends, GUARD_MAX_CLOSE_SENDS);
  }

//--- G7: riga del pannello
string GuardPanelText()
  {
   if(!InpGuardOn) return("Guardia OFF (trading come la build Q2)");
   string r = g_gReason;
   if(g_gMarginWait && g_entryDeadline>0 && GuardNow() >= g_entryDeadline)
      r = "finestra chiusa: margine mai sufficiente";
   return(StringFormat("Guardia ON | richieste oggi %d/%d | ingressi inviati %d/%d | chiusure rifiutate %d | ultimo rifiuto %s | %s",
                       g_gReqToday, InpGuardDailyBudget, g_gEntrySends, GUARD_MAX_ENTRY_SENDS, g_gCloseFails,
                       (g_gLastRetcode>0 ? IntegerToString(g_gLastRetcode) : "-"),
                       (r=="" ? "ok" : r)));
  }

//=== MODULO GRAFICO =================================================
string VName(string tag){ return StringFormat("ORB_%s_%d", tag, g_lastDayId); }

void DrawVLine(string tag, datetime t, color clr, ENUM_LINE_STYLE style, string tip)
  {
   if(!g_canDraw) return;
   string n=VName(tag);
   ObjectDelete(0,n);
   if(ObjectCreate(0,n,OBJ_VLINE,0,t,0))
     {
      ObjectSetInteger(0,n,OBJPROP_COLOR,clr);
      ObjectSetInteger(0,n,OBJPROP_STYLE,style);
      ObjectSetInteger(0,n,OBJPROP_WIDTH,1);
      ObjectSetInteger(0,n,OBJPROP_BACK,true);
      ObjectSetInteger(0,n,OBJPROP_SELECTABLE,false);
      ObjectSetString(0,n,OBJPROP_TOOLTIP,tip);
     }
  }

void DrawHSeg(string tag, datetime t1, datetime t2, double p, color clr,
              ENUM_LINE_STYLE style, int width, string tip)
  {
   if(!g_canDraw) return;
   string n=VName(tag);
   ObjectDelete(0,n);
   if(ObjectCreate(0,n,OBJ_TREND,0,t1,p,t2,p))
     {
      ObjectSetInteger(0,n,OBJPROP_COLOR,clr);
      ObjectSetInteger(0,n,OBJPROP_STYLE,style);
      ObjectSetInteger(0,n,OBJPROP_WIDTH,width);
      ObjectSetInteger(0,n,OBJPROP_RAY_RIGHT,false);
      ObjectSetInteger(0,n,OBJPROP_BACK,false);
      ObjectSetInteger(0,n,OBJPROP_SELECTABLE,false);
      ObjectSetString(0,n,OBJPROP_TOOLTIP,tip);
     }
  }

void DrawRectC1(datetime t1, double p1, datetime t2, double p2, color clr, string tip)
  {
   if(!g_canDraw) return;
   string n=VName("c1");
   ObjectDelete(0,n);
   if(ObjectCreate(0,n,OBJ_RECTANGLE,0,t1,p1,t2,p2))
     {
      ObjectSetInteger(0,n,OBJPROP_COLOR,clr);
      ObjectSetInteger(0,n,OBJPROP_STYLE,STYLE_SOLID);
      ObjectSetInteger(0,n,OBJPROP_WIDTH,2);
      ObjectSetInteger(0,n,OBJPROP_FILL,false);
      ObjectSetInteger(0,n,OBJPROP_BACK,false);
      ObjectSetInteger(0,n,OBJPROP_SELECTABLE,false);
      ObjectSetString(0,n,OBJPROP_TOOLTIP,tip);
     }
  }

void DrawLabelAt(string tag, datetime t, double p, string txt, color clr, int fsize)
  {
   if(!g_canDraw) return;
   string n=VName(tag);
   ObjectDelete(0,n);
   if(ObjectCreate(0,n,OBJ_TEXT,0,t,p))
     {
      ObjectSetString(0,n,OBJPROP_TEXT,txt);
      ObjectSetInteger(0,n,OBJPROP_COLOR,clr);
      ObjectSetInteger(0,n,OBJPROP_FONTSIZE,fsize);
      ObjectSetInteger(0,n,OBJPROP_ANCHOR,ANCHOR_LEFT);
      ObjectSetInteger(0,n,OBJPROP_SELECTABLE,false);
     }
  }

void DrawEntryArrow(bool isLong, datetime t, double p)
  {
   if(!g_canDraw) return;
   string n=VName("arrow");
   ObjectDelete(0,n);
   if(ObjectCreate(0,n,isLong?OBJ_ARROW_BUY:OBJ_ARROW_SELL,0,t,p))
     {
      ObjectSetInteger(0,n,OBJPROP_COLOR,isLong?clrLimeGreen:clrOrangeRed);
      ObjectSetInteger(0,n,OBJPROP_WIDTH,2);
      ObjectSetInteger(0,n,OBJPROP_SELECTABLE,false);
     }
  }

void DrawStopHit(datetime t, double p)
  {
   if(!g_canDraw) return;
   string n=VName("stophit");
   ObjectDelete(0,n);
   if(ObjectCreate(0,n,OBJ_ARROW,0,t,p))
     {
      ObjectSetInteger(0,n,OBJPROP_ARROWCODE,251);
      ObjectSetInteger(0,n,OBJPROP_COLOR,clrRed);
      ObjectSetInteger(0,n,OBJPROP_WIDTH,2);
      ObjectSetInteger(0,n,OBJPROP_SELECTABLE,false);
     }
   DrawLabelAt("stophitlbl", t, p, "STOP HIT", clrRed, 8);
  }

//=== ORDINI =========================================================
void CloseAll(string reason)
  {
   g_selfClosing = true;
   bool closedAny = false;
   for(int i=PositionsTotal()-1; i>=0; i--)
     {
      ulong tk = PositionGetTicket(i);
      if(tk==0) continue;
      if(PositionGetString(POSITION_SYMBOL)==_Symbol &&
         PositionGetInteger(POSITION_MAGIC)==InpMagic)
        {
         //--- GUARDIA (build R) G6: dopo una chiusura rifiutata si aspetta
         //    (nessuna richiesta), con un tetto giornaliero; SL e TP restano
         //    sul server. Con la guardia spenta: come la Q2.
         if(!GuardCanClose())
            continue;
         bool okC = g_trade.PositionClose(tk);
         GuardAfterClose(okC);
         if(!okC)
            PrintFormat("[ORB] ERRORE chiusura ticket %I64u: %d", tk, (int)g_trade.ResultRetcode());
         else
           {
            closedAny=true;
            PrintFormat("[ORB] Posizione chiusa (%s)", reason);
           }
        }
     }
   if(closedAny)
     {
      double px = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      DrawLabelAt("exit", TimeCurrent(), px, reason, clrDodgerBlue, 8);
      g_trackOpen=false;
     }
   g_selfClosing=false;
   g_lastReason=reason;
  }

//=== SIZING =========================================================
double LossPerLot(double slDistance)
  {
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(tickValue<=0 || tickSize<=0 || slDistance<=0) return 0.0;
   return slDistance/tickSize*tickValue;
  }

double RiskMoneyTarget(bool verbose=true)
  {
   if(InpRiskMode==RISK_FIXED_USD)
      return(InpRiskFixedUSD);
   if(InpRiskMode==RISK_PCT_BAL)
      return(AccountInfoDouble(ACCOUNT_BALANCE)*InpRiskPct/100.0);

   //--- RISK_BUFFER: frazione del margine residuo sopra il livello di fallimento.
   //    Avvicinandosi al floor la size si contrae da sola; allontanandosi cresce.
   double eq  = AccountInfoDouble(ACCOUNT_EQUITY);
   double buf = eq - InpFloorEquity;
   if(buf <= 0.0)
     {
      if(verbose) Print("[ORB] BUFFER esaurito: equity <= floor. Nessun nuovo trade.");
      return(0.0);
     }
   double r = buf*InpBufferPct/100.0;
   if(InpBufferCapUSD > 0.0 && r > InpBufferCapUSD) r = InpBufferCapUSD;
   return(r);
  }

double CalcLots(double slDistance)
  {
   double riskMoney  = RiskMoneyTarget();
   double lossPerLot = LossPerLot(slDistance);
   if(lossPerLot<=0)
     {
      Print("[ORB] CalcLots: dati simbolo non validi");
      return 0.0;
     }
   double lots = NormVol(riskMoney/lossPerLot);
   double minL = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxL = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);

   if(lots<minL)
     {
      double minRisk = minL*lossPerLot;
      if(minRisk <= riskMoney*InpMaxRiskOvershoot)
        {
         PrintFormat("[ORB] Lotto minimo %.2f: rischio %.2f vs target %.2f (overshoot ok)", minL, minRisk, riskMoney);
         lots=minL;
        }
      else
        {
         PrintFormat("[ORB] SKIP: lotto minimo %.2f rischierebbe %.2f > %.2f", minL, minRisk, riskMoney*InpMaxRiskOvershoot);
         return 0.0;
        }
     }
   if(lots>maxL) lots=maxL;
   return lots;
  }

// Testo della modalita' rischio EFFETTIVA (il bug della build F era qui:
// stampava sempre '% balance' anche con RISK_BUFFER attivo).
string RiskModeText()
  {
   if(InpRiskMode==RISK_FIXED_USD)
      return(StringFormat("%.0f$ fissi", InpRiskFixedUSD));
   if(InpRiskMode==RISK_PCT_BAL)
      return(StringFormat("%.2f%% balance = %.0f$", InpRiskPct,
                          AccountInfoDouble(ACCOUNT_BALANCE)*InpRiskPct/100.0));
   return(StringFormat("BUFFER %.2f%% x (equity-%.0f), cap %.0f$ -> %.0f$ per trade",
                       InpBufferPct, InpFloorEquity, InpBufferCapUSD, RiskMoneyTarget(false)));
  }

//=== NEWS ===========================================================
void LoadNews()
  {
   g_newsCount=0;
   if(!InpUseNews) return;
   int h = FileOpen(InpNewsCSVName, FILE_READ|FILE_TXT|FILE_ANSI|FILE_SHARE_READ|FILE_COMMON);
   if(h==INVALID_HANDLE)
     {
      Print("[ORB] WARNING: news CSV non trovato in Common\\Files -> filtro news inattivo");
      return;
     }
   while(!FileIsEnding(h) && g_newsCount<MAX_NEWS)
     {
      string line = FileReadString(h);
      StringTrimLeft(line);
      StringTrimRight(line);
      if(line=="") continue;
      if(StringGetCharacter(line,0)=='#') continue;
      string parts[];
      if(StringSplit(line, ';', parts)<1) continue;
      string dandt[];
      if(StringSplit(parts[0], ' ', dandt)!=2) continue;
      string dd[];  if(StringSplit(dandt[0], '.', dd)!=3) continue;
      string tt[];  if(StringSplit(dandt[1], ':', tt)!=2) continue;
      int y  = (int)StringToInteger(dd[0]);
      int mo = (int)StringToInteger(dd[1]);
      int da = (int)StringToInteger(dd[2]);
      int hh = (int)StringToInteger(tt[0]);
      int mi = (int)StringToInteger(tt[1]);
      if(y<2000 || mo<1 || mo>12 || da<1 || da>31) continue;
      g_news[g_newsCount++] = NYToServer(y, mo, da, hh, mi);
     }
   FileClose(h);
   PrintFormat("[ORB] News caricate: %d da %s (orari NY convertiti in ora server)", g_newsCount, InpNewsCSVName);
  }

void CheckNewsClose(datetime now)
  {
   if(!InpUseNews || g_newsCount==0) return;
   if(!HasPosition()) return;
   for(int i=0; i<g_newsCount; i++)
     {
      if(now >= g_news[i]-InpNewsCloseMinBefore*60 && now < g_news[i])
        {
         PrintFormat("[ORB] Chiusura pre-news (news alle %s server)", TimeToString(g_news[i], TIME_DATE|TIME_MINUTES));
         CloseAll("Chiusura pre-news");
         return;
        }
     }
  }

//=== FILTRI GIORNATA ================================================
// RVOL: tick volume candela 1 di oggi vs media candele 1 dei giorni precedenti
double GetRVOL(datetime b1time, long vol1)
  {
   if(vol1<=0) return -1;
   int found=0; double sum=0;
   for(int d=1; d<=40 && found<InpRVOLLookback; d++)
     {
      datetime probeDay = (datetime)((long)b1time - (long)d*86400);
      datetime po = SessionOpenForDate(probeDay);
      int sh = iBarShift(_Symbol, InpORTimeframe, po, true);
      if(sh<0) continue;
      if(iTime(_Symbol, InpORTimeframe, sh)!=po) continue;
      long v = iVolume(_Symbol, InpORTimeframe, sh);
      if(v<=0) continue;
      sum += (double)v;
      found++;
     }
   if(found < MathMax(5, InpRVOLLookback/2)) return -1; // storia insufficiente
   double avg = sum/found;
   if(avg<=0) return -1;
   return (double)vol1/avg;
  }

// Sanity check: la candela di apertura deve avere volume anomalo vs l'ora precedente
void OpenVolumeSanity(int shiftC1, long vol1)
  {
   double sum=0; int n=0;
   for(int k=1; k<=12; k++)
     {
      long v = iVolume(_Symbol, InpORTimeframe, shiftC1+k);
      if(v>0){ sum+=(double)v; n++; }
     }
   if(n>=6 && (double)vol1 < 1.5*(sum/n))
      Print("[ORB] *** WARNING: volume candela apertura NON anomalo rispetto all'ora precedente: possibile ORARIO SESSIONE ERRATO ***");
  }

//=== LOGICA GIORNALIERA =============================================
void OnNewDay(int dayId, datetime now)
  {
   GuardNewDay();   // build R: contatori della guardia azzerati PRIMA della chiusura catch-all
   int posDay = MyPositionDayId();
   if(posDay>0 && posDay!=dayId)
     {
      Print("[ORB] WARNING: posizione aperta da un giorno precedente. Chiusura catch-all.");
      CloseAll("catch-all nuovo giorno");
     }
   else if(posDay==dayId)
      Print("[ORB] Riavvio con posizione aperta di oggi: lasciata correre (SL/TP sono sul server).");
   g_lastDayId    = dayId;
   g_dailyRefEq   = AccountInfoDouble(ACCOUNT_EQUITY);
   g_dailyBlocked = false;
   g_doneToday    = false;
   g_c1Drawn      = false;
   g_rvolToday    = -1;
   g_eodTries     = 0;
   g_alignGapR    = 0.0;
   g_alignVotes   = -1;

   g_sessOpen      = SessionOpenForDate(now);
   int tfSec       = PeriodSeconds(InpORTimeframe);
   g_entryDeadline = g_sessOpen + 2*tfSec;

   // --- Mezza giornata (solo calendario USA): chiusura 13:00 ET
   int sessionMin = InpSessionMinutes;
   if(HalfDayToday(now))
     {
      sessionMin = 210;
      PrintFormat("[ORB] Giorno %d: MEZZA GIORNATA USA -> chiusura anticipata 13:00 ET.", dayId);
     }
   g_sessCloseCut  = g_sessOpen + (sessionMin - InpMinutesBeforeClose)*60;

   DrawVLine("open", g_sessOpen, clrSilver, STYLE_DOT, "Apertura 9:30 NY (ora server)");
   DrawVLine("cut",  g_sessCloseCut, clrDimGray, STYLE_DASH, "Chiusura forzata EoD");

   PrintFormat("[ORB] === Giorno %d | Open (server): %s | Cut: %s | EqRef: %.2f | ATR(D1): %.2f ===",
               dayId, TimeToString(g_sessOpen, TIME_DATE|TIME_MINUTES),
               TimeToString(g_sessCloseCut, TIME_MINUTES), g_dailyRefEq, DailyATR());

   // --- Giorno di borsa CHIUSA (calendario attivo): nessun trade oggi
   if(MarketClosedToday(now))
     {
      g_doneToday  = true;
      g_lastReason = "skip: borsa chiusa";
      if(CalendarIsDE())
         PrintFormat("[ORB] Giorno %d: BORSA CHIUSA (calendario XETRA) -> nessun trade.", dayId);
      else
         PrintFormat("[ORB] Giorno %d: BORSA CHIUSA (calendario NYSE) -> nessun trade.", dayId);
     }
  }

void CheckGuards()
  {
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);

   //--- TARGET DI PROFITTO: oltre il target il profitto vale ZERO, perche' la
   //    fase successiva riparte dal capitale iniziale. Fermarsi e' strettamente
   //    dominante: si evita di restituire il guadagno gia' acquisito.
   if(InpUseProfitTarget && !g_targetReached && g_baseline>0 &&
      eq >= g_baseline + InpProfitTargetUSD + InpTargetBufferUSD)
     {
      if(HasPosition()) CloseAll("TARGET DI FASE RAGGIUNTO");
      g_targetReached = true;
      g_doneToday     = true;
      DrawLabelAt("target", TimeCurrent(), SymbolInfoDouble(_Symbol,SYMBOL_BID),
                  ">>> TARGET RAGGIUNTO - TRADING FERMO <<<", clrLime, 10);
      PrintFormat("[ORB] *** TARGET DI FASE RAGGIUNTO: equity %.2f >= baseline %.2f + %.0f. "
                  "Posizione chiusa, nessun nuovo trade. ***", eq, g_baseline, InpProfitTargetUSD);
      return;
     }

   if(!g_totalBlocked && g_baseline>0 && eq <= g_baseline - InpTotalLossCapUSD)
     {
      CloseAll("TOTAL LOSS CAP");
      g_totalBlocked=true;
      DrawLabelAt("totalcap", TimeCurrent(), SymbolInfoDouble(_Symbol,SYMBOL_BID),
                  ">>> TOTAL CAP - EVALUATION FAILED <<<", clrRed, 10);
      PrintFormat("[ORB] *** TOTAL LOSS CAP (%.0f USD) RAGGIUNTO. Equity %.2f / baseline %.2f. TRADING DISABILITATO. ***",
                  InpTotalLossCapUSD, eq, g_baseline);
      return;
     }

   if(!g_dailyBlocked && g_dailyRefEq>0 && eq <= g_dailyRefEq - InpDailyLossCapUSD)
     {
      CloseAll("DAILY LOSS CAP");
      g_dailyBlocked=true;
      DrawLabelAt("dailycap", TimeCurrent(), SymbolInfoDouble(_Symbol,SYMBOL_BID),
                  "DAILY CAP", clrOrangeRed, 9);
      PrintFormat("[ORB] ** DAILY LOSS CAP (%.0f USD) raggiunto. Equity %.2f / rif %.2f. Stop fino a domani. **",
                  InpDailyLossCapUSD, eq, g_dailyRefEq);
     }
  }

//=== GESTIONE POSIZIONE (parziale / BE / trailing) ==================
void ManagePosition(datetime now)
  {
   ulong tk; double vol; long ptype; double popen, psl;
   if(!GetMyPosition(tk, vol, ptype, popen, psl)) return;
   if(g_trackRdist<=0) return;

   bool isLong = (ptype==POSITION_TYPE_BUY);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double stopsPts = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL)*_Point;

   double curR = isLong ? (bid-g_trackEntry)/g_trackRdist
                        : (g_trackEntry-ask)/g_trackRdist;

   //--- PARZIALE + BREAKEVEN
   if(InpUsePartial && !g_partialDone && curR >= InpPartialTriggerR)
     {
      double frac = (InpPartialFrac==PFRAC_1_4 ? 0.25 : (InpPartialFrac==PFRAC_1_3 ? 1.0/3.0 : 0.5));
      double minL = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
      double closeVol = NormVol(vol*frac);
      double resid = vol - closeVol;
      bool partialExecuted=false;

      if(closeVol>=minL && resid>=minL-1e-9)
        {
         bool okP = false;                                  // build R: richiesta contata (G1)
         if(GuardCanSend("chiusura parziale"))
           {
            okP = g_trade.PositionClosePartial(tk, closeVol);
            GuardAfterSend(okP);
           }
         if(okP)
           {
            partialExecuted=true;
            PrintFormat("[ORB] PARZIALE: chiusi %.2f lotti a +%.2fR (residuo %.2f)", closeVol, curR, resid);
            DrawLabelAt("tp1", now, isLong?bid:ask,
                        StringFormat("TP parziale %.0f%%  @ +%.1fR", frac*100, InpPartialTriggerR),
                        clrDeepSkyBlue, 8);
           }
         else
            PrintFormat("[ORB] ERRORE parziale (retcode %d) - procedo comunque a BE", (int)g_trade.ResultRetcode());
        }
      else
         Print("[ORB] Parziale saltato (lotto minimo): applico solo breakeven");

      // Breakeven con buffer
      double newSL = isLong ? g_trackEntry + InpBEBufferPoints*_Point
                            : g_trackEntry - InpBEBufferPoints*_Point;
      newSL = NormPrice(newSL);
      bool okDist = isLong ? (newSL < bid - stopsPts) : (newSL > ask + stopsPts);
      bool okBE = false;                                    // build R: richiesta contata (G1)
      if(okDist && GuardCanSend("breakeven"))
        {
         okBE = g_trade.PositionModify(tk, newSL, 0.0);
         GuardAfterSend(okBE);
        }
      if(okBE)
        {
         g_beDone=true;
         g_curSL=newSL;
         g_partialDone=true;
         g_lastBarTime = iTime(_Symbol, InpORTimeframe, 0);
         DrawHSeg("slbe", now, g_sessCloseCut, newSL, clrGoldenrod, STYLE_DASH, 1, "Stop a breakeven");
         PrintFormat("[ORB] BREAKEVEN: SL spostato a %.2f (buffer %.1f punti)", newSL, InpBEBufferPoints);
        }
      else
        {
         // se il parziale e' andato ma il BE no, non ripetere il parziale: segna fatto e ritenta solo il BE
         if(partialExecuted) g_partialDone=true;
         Print("[ORB] BE rinviato (stops level o modify fallita): ritento al prossimo tick");
        }
      return;
     }

   //--- solo BE mancante (parziale gia' fatto, modify fallita prima)
   if(InpUsePartial && g_partialDone && !g_beDone)
     {
      double newSL = isLong ? g_trackEntry + InpBEBufferPoints*_Point
                            : g_trackEntry - InpBEBufferPoints*_Point;
      newSL = NormPrice(newSL);
      bool okDist = isLong ? (newSL < bid - stopsPts) : (newSL > ask + stopsPts);
      bool okBE2 = false;                                   // build R: richiesta contata (G1)
      if(okDist && GuardCanSend("breakeven"))
        {
         okBE2 = g_trade.PositionModify(tk, newSL, 0.0);
         GuardAfterSend(okBE2);
        }
      if(okBE2)
        {
         g_beDone=true;
         g_curSL=newSL;
         g_lastBarTime = iTime(_Symbol, InpORTimeframe, 0);
         DrawHSeg("slbe", now, g_sessCloseCut, newSL, clrGoldenrod, STYLE_DASH, 1, "Stop a breakeven");
         PrintFormat("[ORB] BREAKEVEN (ritentato): SL a %.2f", newSL);
        }
      return;
     }

   //--- TRAILING (solo dopo BE, solo se attivo, su nuova barra)
   if(InpUseTrailing && g_beDone)
     {
      datetime bt = iTime(_Symbol, InpORTimeframe, 0);
      if(bt!=g_lastBarTime)
        {
         g_lastBarTime=bt;
         double hPrev = iHigh(_Symbol, InpORTimeframe, 1);
         double lPrev = iLow (_Symbol, InpORTimeframe, 1);
         if(hPrev>0) g_hh = MathMax(g_hh, hPrev);
         if(lPrev>0) g_ll = (g_ll<=0 ? lPrev : MathMin(g_ll, lPrev));

         double atr = DailyATR();
         if(atr>0)
           {
            double dist = atr*InpTrailATRPct/100.0;
            double newTrail = isLong ? g_hh-dist : g_ll+dist;
            newTrail = NormPrice(newTrail);
            double tsz = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
            if(tsz<=0) tsz=_Point;
            bool improves = isLong ? (newTrail > g_curSL + tsz) : (newTrail < g_curSL - tsz);
            bool okDist2  = isLong ? (newTrail < bid - stopsPts) : (newTrail > ask + stopsPts);
            if(improves && okDist2)
              {
               bool okT = false;                            // build R: richiesta contata (G1)
               if(GuardCanSend("trailing"))
                 {
                  okT = g_trade.PositionModify(tk, newTrail, 0.0);
                  GuardAfterSend(okT);
                 }
               if(okT)
                 {
                  g_curSL=newTrail;
                  DrawHSeg("sltrail", now, g_sessCloseCut, newTrail, clrMediumOrchid, STYLE_DOT, 1, "Trailing stop");
                  PrintFormat("[ORB] TRAILING: SL -> %.2f", newTrail);
                 }
              }
           }
        }
     }
  }

//=== FILTRO DI ALLINEAMENTO (build Q) ===============================
// Il segnale ORB entra solo se la candela 1 chiude dalla stessa parte
// della deriva dell'ora precedente, staccata di almeno InpAlignBufferR
// volte la distanza di stop. Il cuscinetto e' espresso in R e non in
// punti perche' deve allargarsi e stringersi con la volatilita', come
// fa gia' lo stop: 0,15R sono ~5,5 punti con ATR 370 e ~8,8 con ATR 590.
string AlignRefText(ENUM_RIF_ALLIN r)
  {
   switch(r)
     {
      case RIF_EMA:      return "EMA";
      case RIF_SMA:      return "SMA";
      case RIF_CHIUSURA_N:  return "chiusura N barre fa";
      case RIF_META_RANGE: return "meta' range";
      case RIF_ROTTURA: return "rottura range";
     }
   return "?";
  }

string AlignModeText()
  {
   if(InpAlignMode==FILTRO_OFF)    return "OFF (build P)";
   if(InpAlignMode==FILTRO_SINGOLO)
      return StringFormat("SINGOLO %s(%d), cuscinetto %.2fR",
                          AlignRefText(InpAlignRef), InpAlignPeriod, InpAlignBufferR);
   return StringFormat("ENSEMBLE min %d voti su 5, periodo %d, cuscinetto %.2fR",
                       InpAlignMinVotes, InpAlignPeriod, InpAlignBufferR);
  }

//--- livello di riferimento. shift = indice della candela 1.
//    Ritorna false se il dato non e' disponibile: in quel caso il filtro
//    NON viene applicato, come gia' fa il filtro RVOL con storia corta.
bool AlignLevel(ENUM_RIF_ALLIN ref, int period, int shift, bool goLong, double &lvl)
  {
   lvl = 0.0;
   if(period < 1) return false;

   if(ref==RIF_EMA || ref==RIF_SMA)
     {
      int h = (ref==RIF_EMA ? g_hAlignEMA : g_hAlignSMA);
      if(h==INVALID_HANDLE) return false;
      double buf[];
      if(CopyBuffer(h, 0, shift, 1, buf)!=1) return false;
      lvl = buf[0];
      return (lvl>0.0);
     }

   if(ref==RIF_CHIUSURA_N)
     {
      lvl = iClose(_Symbol, InpORTimeframe, shift+period);
      return (lvl>0.0);
     }

   if(ref==RIF_META_RANGE)
     {
      int ih = iHighest(_Symbol, InpORTimeframe, MODE_HIGH, period, shift);
      int il = iLowest (_Symbol, InpORTimeframe, MODE_LOW,  period, shift);
      if(ih<0 || il<0) return false;
      double hh = iHigh(_Symbol, InpORTimeframe, ih);
      double ll = iLow (_Symbol, InpORTimeframe, il);
      if(hh<=0.0 || ll<=0.0) return false;
      lvl = (hh+ll)/2.0;
      return true;
     }

   if(ref==RIF_ROTTURA)
     {
      //--- SIMMETRICO: massimo delle N barre precedenti per il long,
      //    minimo per lo short. La versione asimmetrica (sempre il
      //    massimo) rendeva questo voto vero nel 99,9% degli short.
      if(goLong)
        {
         int ih = iHighest(_Symbol, InpORTimeframe, MODE_HIGH, period, shift+1);
         if(ih<0) return false;
         lvl = iHigh(_Symbol, InpORTimeframe, ih);
        }
      else
        {
         int il = iLowest(_Symbol, InpORTimeframe, MODE_LOW, period, shift+1);
         if(il<0) return false;
         lvl = iLow(_Symbol, InpORTimeframe, il);
        }
      return (lvl>0.0);
     }

   return false;
  }

//--- true = il riferimento approva. gapR riceve lo scarto misurato in R.
bool AlignPass(ENUM_RIF_ALLIN ref, int period, int shift, bool goLong,
               double c1close, double distR, double &gapR)
  {
   gapR = 0.0;
   double lvl;
   if(!AlignLevel(ref, period, shift, goLong, lvl)) return true;   // dato assente -> non filtro
   if(distR<=0.0) return true;
   gapR = (goLong ? c1close-lvl : lvl-c1close)/distR;
   return (gapR > InpAlignBufferR);
  }

//--- ensemble: 5 riferimenti indipendenti, un voto ciascuno.
int AlignVotes(int period, int shift, bool goLong, double c1close, double distR)
  {
   int v = 0;
   double g;
   int half = (int)MathMax(1, period/2);
   if(AlignPass(RIF_EMA,      period, shift, goLong, c1close, distR, g)) v++;
   if(AlignPass(RIF_CHIUSURA_N,  period, shift, goLong, c1close, distR, g)) v++;
   if(AlignPass(RIF_CHIUSURA_N,  half,   shift, goLong, c1close, distR, g)) v++;
   if(AlignPass(RIF_META_RANGE, period, shift, goLong, c1close, distR, g)) v++;
   if(AlignPass(RIF_ROTTURA, period, shift, goLong, c1close, distR, g)) v++;
   return v;
  }

//=== INGRESSO =======================================================
void TryEnter(datetime now)
  {
   int tfSec = PeriodSeconds(InpORTimeframe);

   //--- GUARDIA (build R): nei ricontrolli (attesa del margine o pausa fra
   //    due invii) il segnale si rivaluta al massimo una volta al secondo e
   //    le sue righe non si ristampano. Con la guardia spenta: come la Q2.
   bool gRecheck = (InpGuardOn && g_gSignalLogged);
   if(gRecheck)
     {
      datetime tg = GuardNow();
      if(tg <= g_gLastRecheck) return;
      g_gLastRecheck = tg;
     }

   int shift = iBarShift(_Symbol, InpORTimeframe, g_sessOpen, true);
   if(shift<0)
     {
      shift = iBarShift(_Symbol, InpORTimeframe, g_sessOpen, false);
      if(shift<0) return;
      datetime bt = iTime(_Symbol, InpORTimeframe, shift);
      if(bt<g_sessOpen || bt>=g_sessOpen+tfSec) return;
     }

   datetime b1time = iTime(_Symbol, InpORTimeframe, shift);
   if(now < b1time+tfSec) return; // candela 1 non chiusa

   double o1=iOpen(_Symbol,InpORTimeframe,shift);
   double c1=iClose(_Symbol,InpORTimeframe,shift);
   double h1=iHigh(_Symbol,InpORTimeframe,shift);
   double l1=iLow (_Symbol,InpORTimeframe,shift);
   long   v1=iVolume(_Symbol,InpORTimeframe,shift);
   double range=h1-l1;

   string c1tip = StringFormat("C1: O=%s H=%s L=%s C=%s V=%I64d",
                  DoubleToString(o1,_Digits), DoubleToString(h1,_Digits),
                  DoubleToString(l1,_Digits), DoubleToString(c1,_Digits), v1);

   if(!gRecheck) OpenVolumeSanity(shift, v1);

   if(range<=0)
     {
      g_doneToday=true; g_lastReason="skip: range nullo";
      if(!g_c1Drawn){ DrawRectC1(b1time,h1,b1time+tfSec,l1,clrGold,c1tip); g_c1Drawn=true; }
      DrawLabelAt("skip", b1time, h1, "SKIP: range nullo", clrGold, 8);
      Print("[ORB] SKIP: range nullo");
      return;
     }

   //--- doji
   double body=MathAbs(c1-o1);
   if(body < range*InpMinBodyPctRange/100.0)
     {
      g_doneToday=true; g_lastReason="skip: doji";
      if(!g_c1Drawn){ DrawRectC1(b1time,h1,b1time+tfSec,l1,clrGold,c1tip); g_c1Drawn=true; }
      DrawLabelAt("skip", b1time, h1+range*0.3, "SKIP: doji", clrGold, 8);
      PrintFormat("[ORB] SKIP: doji (body %.1f%% del range)", body/range*100.0);
      return;
     }

   //--- FILTRO AMPIEZZA (range gate)
   double atr = DailyATR();
   if(atr<=0)
     {
      g_doneToday=true; g_lastReason="skip: ATR n/d";
      DrawLabelAt("skip", b1time, h1+range*0.3, "SKIP: ATR n/d", clrGold, 8);
      Print("[ORB] SKIP: ATR daily non disponibile");
      return;
     }
   double rangePct = range/atr*100.0;
   if(InpUseRangeGate && (rangePct<InpRangeMinPctATR || rangePct>InpRangeMaxPctATR))
     {
      g_doneToday=true; g_lastReason=StringFormat("skip: ampiezza %.1f%%ATR", rangePct);
      if(!g_c1Drawn){ DrawRectC1(b1time,h1,b1time+tfSec,l1,clrGold,c1tip); g_c1Drawn=true; }
      DrawLabelAt("skip", b1time, h1+range*0.3,
                  StringFormat("SKIP: ampiezza %.1f%% ATR", rangePct), clrGold, 8);
      PrintFormat("[ORB] SKIP: ampiezza candela1 %.1f%% ATR fuori da [%.1f - %.1f]",
                  rangePct, InpRangeMinPctATR, InpRangeMaxPctATR);
      return;
     }

   //--- FILTRO RVOL
   if(InpUseRVOL)
     {
      g_rvolToday = GetRVOL(b1time, v1);
      if(g_rvolToday>=0 && g_rvolToday < InpRVOLThreshold)
        {
         g_doneToday=true; g_lastReason=StringFormat("skip: RVOL %.2f", g_rvolToday);
         if(!g_c1Drawn){ DrawRectC1(b1time,h1,b1time+tfSec,l1,clrGold,c1tip); g_c1Drawn=true; }
         DrawLabelAt("skip", b1time, h1+range*0.3,
                     StringFormat("SKIP: RVOL %.2f < %.2f", g_rvolToday, InpRVOLThreshold), clrGold, 8);
         PrintFormat("[ORB] SKIP: RVOL %.2f sotto soglia %.2f", g_rvolToday, InpRVOLThreshold);
         return;
        }
      if(g_rvolToday<0)
         Print("[ORB] RVOL: storia insufficiente, filtro non applicato oggi");
     }

   bool goLong = (c1>o1);

   if(!g_c1Drawn)
     {
      DrawRectC1(b1time,h1,b1time+tfSec,l1, goLong?clrLimeGreen:clrOrangeRed, c1tip);
      g_c1Drawn=true;
     }

   if((goLong && !InpAllowLong) || (!goLong && !InpAllowShort))
     {
      g_doneToday=true; g_lastReason="skip: direzione off";
      DrawLabelAt("skip", b1time, h1+range*0.3, "SKIP: direzione off", clrGold, 8);
      return;
     }

   //--- FILTRO DI ALLINEAMENTO (build Q). Con FILTRO_OFF non entra qui.
   //    distR usa lo stop TEORICO (ATR x InpStopATRPct), non quello
   //    eventualmente allargato dallo stops level: e' l'unita' con cui
   //    il filtro e' stato validato.
   if(InpAlignMode != FILTRO_OFF)
     {
      double distR = atr*InpStopATRPct/100.0;
      if(InpAlignMode == FILTRO_SINGOLO)
        {
         double gapR;
         bool ok = AlignPass(InpAlignRef, InpAlignPeriod, shift, goLong, c1, distR, gapR);
         g_alignGapR = gapR;
         if(!ok)
           {
            g_doneToday=true;
            g_lastReason=StringFormat("skip: allineamento %.2fR", gapR);
            DrawLabelAt("skip", b1time, h1+range*0.3,
                        StringFormat("SKIP: allineamento %.2fR", gapR), clrGold, 8);
            PrintFormat("[ORB] SKIP: allineamento %s scarto %.2fR sotto il cuscinetto %.2fR",
                        AlignRefText(InpAlignRef), gapR, InpAlignBufferR);
            return;
           }
         if(!gRecheck)
            PrintFormat("[ORB] Allineamento OK: %s scarto %.2fR (cuscinetto %.2fR)",
                        AlignRefText(InpAlignRef), gapR, InpAlignBufferR);
        }
      else
        {
         int v = AlignVotes(InpAlignPeriod, shift, goLong, c1, distR);
         g_alignVotes = v;
         if(v < InpAlignMinVotes)
           {
            g_doneToday=true;
            g_lastReason=StringFormat("skip: voti %d su 5", v);
            DrawLabelAt("skip", b1time, h1+range*0.3,
                        StringFormat("SKIP: %d voti su 5", v), clrGold, 8);
            PrintFormat("[ORB] SKIP: ensemble %d voti su 5, minimo richiesto %d",
                        v, InpAlignMinVotes);
            return;
           }
         if(!gRecheck)
            PrintFormat("[ORB] Allineamento OK: ensemble %d voti su 5 (minimo %d)",
                        v, InpAlignMinVotes);
        }
     }

   //--- stop e sizing
   double dist = atr*InpStopATRPct/100.0;
   double minDist = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL)*_Point;
   if(dist<minDist)
     {
      if(!gRecheck)
         PrintFormat("[ORB] Distanza stop %.2f < stops level %.2f: allargata", dist, minDist);
      dist=minDist;
     }

   double ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
   double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID);
   double entry = goLong?ask:bid;
   double sl = NormPrice(goLong? entry-dist : entry+dist);
   double tp = (InpUseTakeProfit && InpTPMultiple>0.0)
               ? NormPrice(goLong? entry+dist*InpTPMultiple : entry-dist*InpTPMultiple)
               : 0.0;

   double lots = CalcLots(dist);
   if(lots<=0)
     {
      g_doneToday=true; g_lastReason="skip: sizing";
      DrawLabelAt("skip", b1time, h1+range*0.3, "SKIP: sizing", clrGold, 8);
      return;
     }

   double spr = SpreadIndexPts();

   //--- MODALITA' OSSERVAZIONE: nessun ordine inviato.
   //    Serve per misurare spread e orario reali sul demo FTMO
   //    lasciando l'EA sul grafico con Algo Trading spento.
   if(!TradingIsLive())
     {
      if(spr>0){ g_sprSum+=spr; g_sprN++; if(spr>g_sprMax) g_sprMax=spr; }
      g_doneToday=true;
      g_lastReason="OSSERVAZIONE: nessun ordine inviato";
      PrintFormat("[ORB] OSSERVAZIONE %s | avrebbe aperto %.2f lotti | entry %.2f | SL %.2f | R$ %.0f | spread %.2f pt indice | rangeC1 %.1f%%ATR",
                  goLong?"LONG":"SHORT", lots, entry, sl, lots*LossPerLot(dist), spr, rangePct);
      DrawLabelAt("skip", b1time, h1+range*0.3,
                  StringFormat("OSSERVAZIONE: %s (spread %.2f)", goLong?"LONG":"SHORT", spr),
                  clrDodgerBlue, 8);
      return;
     }

   //--- GUARDIA (build R) G2-G5: permessi, tetto e pausa, inseguimento,
   //    margine, budget. Se dice di no, nessuna richiesta parte.
   if(InpGuardOn)
     {
      g_gSignalLogged = true;
      if(!GuardPreEntry(goLong, lots, entry))
         return;
      if(!GuardCanSend("ingresso"))
        {
         GuardCloseDay("budget giornaliero di richieste esaurito");
         return;
        }
     }

   bool ok = goLong
             ? g_trade.Buy (lots,_Symbol,0.0,sl,tp,BUILD_ID)
             : g_trade.Sell(lots,_Symbol,0.0,sl,tp,BUILD_ID);

   bool entryOK = (ok && (g_trade.ResultRetcode()==TRADE_RETCODE_DONE ||
                          g_trade.ResultRetcode()==TRADE_RETCODE_PLACED));
   if(InpGuardOn)                                         // G1/G4: invio contato
     {
      g_gEntrySends++;
      g_gLastEntrySend = GuardNow();
      GuardAfterSend(entryOK);
     }

   if(entryOK)
     {
      //--- PREZZO REALE DI ESECUZIONE.
      //    g_trade.ResultPrice() sull'esecuzione di mercato puo' restituire il
      //    prezzo RICHIESTO e non quello ESEGUITO. Verificato in live su FTMO il
      //    04/08/2026: richiesto 29263.78, eseguito 29265.88 (2,10 pt), ma
      //    ResultPrice() ha restituito il richiesto -> slippage loggato 0,00 e
      //    ancoraggio mai scattato. L'unica fonte affidabile del prezzo di
      //    riempimento e' POSITION_PRICE_OPEN letta dal server.
      ulong  tkF; double vF; long tyF; double poF, psF;
      bool   haveF = GetMyPosition(tkF,vF,tyF,poF,psF);

      //--- FIX 5.14 (BUILD P) - ATTESA DELLA POSIZIONE NELLA CACHE DEL TERMINALE.
      //    Quando OrderSend ritorna, la posizione puo' NON essere ancora visibile a
      //    PositionsTotal(): il 21/08/2026 su FTMO l'ordine e' stato eseguito in 204 ms
      //    e il deal e' comparso 1 ms DOPO questa lettura. haveF era false, l'EA e'
      //    ricaduto su ResultPrice() (= prezzo RICHIESTO, trappola 5.3) e l'intero
      //    riancoraggio e' stato saltato IN SILENZIO: rischio effettivo 512,47$ contro
      //    i 474,58$ voluti, e nessuna riga di log a segnalarlo.
      //    Qui si attende la comparsa della posizione, al massimo 1 secondo. La
      //    posizione NON e' scoperta durante l'attesa: SL e TP viaggiano allegati
      //    all'ordine di mercato e sono gia' sul server.
      //    INERTE IN BACKTEST PER COSTRUZIONE: nel tester la posizione e' disponibile
      //    subito e la guardia MQL_TESTER esclude comunque il ramo. La build P e'
      //    quindi identica alla O cella per cella, salvo il commento d'ordine.
      if(!haveF && !MQLInfoInteger(MQL_TESTER))
        {
         for(int kWait=0; kWait<20 && !haveF; kWait++)
           {
            Sleep(50);
            haveF = GetMyPosition(tkF,vF,tyF,poF,psF);
           }
         if(haveF)
            PrintFormat("[ORB] posizione visibile dopo attesa: riancoraggio possibile (fill %.2f)", poF);
         else
            Print("[ORB] *** ATTENZIONE: posizione NON leggibile dopo l'invio -> SL/TP NON riancorati al fill. Rischio effettivo NON garantito. ***");
        }

      double fill  = (haveF && poF>0.0) ? poF : g_trade.ResultPrice();
      if(fill<=0) fill=entry;

      //--- ANCORAGGIO DI STOP E TAKE PROFIT AL PREZZO ESEGUITO.
      //    Stop e TP erano stati calcolati sul prezzo letto PRIMA dell'invio: con
      //    lo slippage la distanza reale |fill-SL| differisce da quella voluta e il
      //    rischio effettivo devia dal target (misurato: 0,80x-1,22x fra p10 e p90).
      //    Riallineandoli al fill il rischio torna quello progettato e il TP torna
      //    esattamente a InpTPMultiple x R.
      if(InpAnchorSLToFill && haveF)
        {
         double slWanted = NormPrice(goLong ? fill-dist : fill+dist);
         double tpWanted = (InpUseTakeProfit && InpTPMultiple>0.0)
                           ? NormPrice(goLong ? fill+dist*InpTPMultiple : fill-dist*InpTPMultiple)
                           : 0.0;
         if(MathAbs(slWanted-sl) > SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_SIZE))
           {
            double bidF = SymbolInfoDouble(_Symbol,SYMBOL_BID);
            double askF = SymbolInfoDouble(_Symbol,SYMBOL_ASK);
            double lvlF = (double)SymbolInfoInteger(_Symbol,SYMBOL_TRADE_STOPS_LEVEL)*_Point;
            bool okF = goLong ? (slWanted < bidF-lvlF) : (slWanted > askF+lvlF);
            bool okM = false;                               // build R: richiesta contata (G1)
            if(okF && GuardCanSend("riallineamento SL/TP"))
              {
               okM = g_trade.PositionModify(tkF, slWanted, tpWanted);
               GuardAfterSend(okM);
              }
            if(okM)
              {
               PrintFormat("[ORB] SL/TP riallineati al fill: SL %.2f -> %.2f | TP %.2f -> %.2f (slippage %.2f pt)",
                           sl, slWanted, tp, tpWanted, MathAbs(fill-entry));
               sl = slWanted;
              }
            else
               PrintFormat("[ORB] SL non riallineabile (stops level): resta %.2f, rischio effettivo %.0f%% del target",
                           sl, MathAbs(fill-sl)/dist*100.0);
           }
        }

      double riskMoney = lots*LossPerLot(MathAbs(fill-sl));

      //--- slippage d'ingresso: positivo = eseguito PEGGIO del prezzo richiesto
      double slip = (goLong ? (fill-entry) : (entry-fill));
      g_slipSum += slip; g_slipN++;
      if(slip>g_slipMax) g_slipMax=slip;

      //--- spread reale nel momento dell'ingresso (punti indice)
      if(spr>0){ g_sprSum+=spr; g_sprN++; if(spr>g_sprMax) g_sprMax=spr; }

      g_doneToday=true;
      g_lastReason = goLong?"LONG aperto":"SHORT aperto";

      g_trackOpen=true; g_trackLong=goLong;
      g_trackEntry=fill; g_trackSL=sl; g_curSL=sl;
      g_trackRdist=MathAbs(fill-sl);
      g_trackTime=now;
      g_partialDone=false; g_beDone=false;
      g_hh=fill; g_ll=fill;
      g_lastBarTime=iTime(_Symbol,InpORTimeframe,0);

      DrawEntryArrow(goLong, now, fill);
      DrawHSeg("entry", now, g_sessCloseCut, fill, goLong?clrLimeGreen:clrOrangeRed, STYLE_SOLID, 2, "Entrata");
      DrawHSeg("sl", now, g_sessCloseCut, sl, clrRed, STYLE_DASH, 1, "Stop loss iniziale");
      DrawLabelAt("info", now, goLong? sl-dist*0.15 : sl+dist*0.15,
                  StringFormat("%s %.2f lotti | R=%.0f$ | stop %.2f (%.0f%% ATR) | RVOL %.2f",
                               goLong?"LONG":"SHORT", lots, riskMoney, dist, InpStopATRPct,
                               g_rvolToday),
                  goLong?clrLimeGreen:clrOrangeRed, 8);

      PrintFormat("[ORB] ENTRY %s | lotti %.2f | fill %.2f | SL %.2f | R$ %.0f | rangeC1 %.1f%%ATR | spread %.2f pt | slip %.2f pt",
                  goLong?"LONG":"SHORT", lots, fill, sl, riskMoney, rangePct, spr, slip);
      if(InpGuardOn)                                      // build R: scarto dal PRIMO segnale (COSTI 1.6)
         PrintFormat("[ORB][GUARDIA] Ingresso all'invio %d di %d | prezzo del primo segnale %.2f | eseguito %.2f | scarto dal segnale %.2f pt | richieste oggi %d/%d",
                     g_gEntrySends, GUARD_MAX_ENTRY_SENDS, g_gFirstPrice, fill,
                     (goLong ? fill-g_gFirstPrice : g_gFirstPrice-fill), g_gReqToday, InpGuardDailyBudget);

      //--- il freno giornaliero deve restare largo rispetto a 1R,
      //    altrimenti chiude il trade prima dello stop (rilevante
      //    solo a equity alta: fase 2 e conto funded).
      if(riskMoney*1.5 > InpDailyLossCapUSD)
         PrintFormat("[ORB] *** ATTENZIONE: rischio %.0f$ per trade contro freno giornaliero %.0f$: il freno puo' anticipare lo stop. Valutare di alzarlo. ***",
                     riskMoney, InpDailyLossCapUSD);
     }
   else if(!InpGuardOn)
      PrintFormat("[ORB] OrderSend fallito (retcode %d). Ritento entro la finestra.", (int)g_trade.ResultRetcode());
   else
      GuardEntryFailed(g_trade.ResultRetcode());           // build R G4: codice letto, tetto ai tentativi
  }

//=== PANNELLO =======================================================
void UpdatePanel()
  {
   string status;
   if(g_targetReached)     status="TARGET RAGGIUNTO - trading fermo";
   else if(g_totalBlocked) status="BLOCCATO (total cap) - FAIL";
   else if(g_dailyBlocked) status="bloccato oggi (daily cap)";
   else if(HasPosition())  status=(g_beDone?"IN POSIZIONE (BE attivo)":"IN POSIZIONE");
   else if(g_doneToday)    status="giorno concluso";
   else                    status="in attesa";

   double eq   = AccountInfoDouble(ACCOUNT_EQUITY);
   double spr  = SpreadIndexPts();
   double dLeft = (g_dailyRefEq>0 ? eq-(g_dailyRefEq-InpDailyLossCapUSD) : 0.0);
   double tLeft = (g_baseline>0   ? eq-(g_baseline-InpTotalLossCapUSD)   : 0.0);

   string trdTxt = InpDryRun ? "DRY RUN (nessun ordine)"
                   : (TradingIsLive() ? "ATTIVO" : "OSSERVAZIONE (algo off)");
   string sprNow = (spr>=0    ? DoubleToString(spr,2)            : "n/d");
   string sprAvg = (g_sprN>0  ? DoubleToString(g_sprSum/g_sprN,2): "n/d");

   Comment(StringFormat(
      "[BUILD %s]  %s  %s  |  orario %s  |  trading %s\n"
      "Open (server): %s | Cut EoD: %s | timer EoD %s\n"
      "Stato: %s | ultimo evento: %s\n"
      "Rischio: %s\n"
      "Equity %.2f | buffer sopra floor %.0f | rif giorno %.2f | baseline %.2f\n"
      "Freni: giorno -%.0f$ (margine %.0f$) | totale -%.0f$ (margine %.0f$)\n"
      "Spread ora %s pt indice | medio all'ingresso %s su %d misure\n"
      "Filtri: ampiezza %s [%.1f-%.1f]%%ATR | RVOL %s | parziale %s | trailing %s | news %d\n"
      "%s",
      BUILD_ID, _Symbol, EnumToString(InpORTimeframe),
      (InpTimeMode==TIME_AUTO_NY?"AUTO-NY":"MANUALE"), trdTxt,
      (g_sessOpen>0     ? TimeToString(g_sessOpen,TIME_DATE|TIME_MINUTES) : "-"),
      (g_sessCloseCut>0 ? TimeToString(g_sessCloseCut,TIME_MINUTES)       : "-"),
      (InpUseEoDTimer?"ON":"off"),
      status, g_lastReason,
      RiskModeText(),
      eq, eq-InpFloorEquity, g_dailyRefEq, g_baseline,
      InpDailyLossCapUSD, dLeft, InpTotalLossCapUSD, tLeft,
      sprNow, sprAvg, g_sprN,
      (InpUseRangeGate?"ON":"off"), InpRangeMinPctATR, InpRangeMaxPctATR,
      (InpUseRVOL?"ON":"off"), (InpUsePartial?"ON":"off"),
      (InpUseTrailing?"ON":"OFF (EoD)"), g_newsCount,
      GuardPanelText()));
  }

//=== EVENT HANDLERS =================================================
int OnInit()
  {
   //--- build R: il budget deve bastare almeno a ingresso, riallineamento e chiusura
   if(InpGuardOn && InpGuardDailyBudget < 10)
     {
      PrintFormat("[ORB][GUARDIA] ERRORE: budget giornaliero %d troppo basso (minimo 10).", InpGuardDailyBudget);
      return INIT_PARAMETERS_INCORRECT;
     }
   g_trade.SetExpertMagicNumber(InpMagic);
   //--- deviation espressa in punti indice -> convertita in punti simbolo
   double ptSize = _Point;
   if(ptSize<=0) ptSize=0.01;
   g_devPoints = (int)MathMax(1.0, MathRound(InpMaxSlipIndexPts/ptSize));
   g_trade.SetDeviationInPoints(g_devPoints);

   uint filling = (uint)SymbolInfoInteger(_Symbol, SYMBOL_FILLING_MODE);
   if((filling & SYMBOL_FILLING_FOK)!=0)      g_trade.SetTypeFilling(ORDER_FILLING_FOK);
   else if((filling & SYMBOL_FILLING_IOC)!=0) g_trade.SetTypeFilling(ORDER_FILLING_IOC);
   else                                        g_trade.SetTypeFilling(ORDER_FILLING_RETURN);

   g_hATR = iATR(_Symbol, PERIOD_D1, InpATRPeriod);
   if(g_hATR==INVALID_HANDLE)
     {
      Print("[ORB] ERRORE: handle ATR non creato");
      return INIT_FAILED;
     }

   //--- build Q: handle delle medie del filtro di allineamento
   if(InpAlignMode != FILTRO_OFF)
     {
      int perA = (int)MathMax(1, InpAlignPeriod);
      g_hAlignEMA = iMA(_Symbol, InpORTimeframe, perA, 0, MODE_EMA, PRICE_CLOSE);
      g_hAlignSMA = iMA(_Symbol, InpORTimeframe, perA, 0, MODE_SMA, PRICE_CLOSE);
      if(g_hAlignEMA==INVALID_HANDLE || g_hAlignSMA==INVALID_HANDLE)
        {
         Print("[ORB] ERRORE: handle delle medie del filtro di allineamento non creato");
         return INIT_FAILED;
        }
     }

   g_canDraw = InpDrawObjects;
   if(MQLInfoInteger(MQL_OPTIMIZATION)) g_canDraw=false;
   if(MQLInfoInteger(MQL_TESTER) && !MQLInfoInteger(MQL_VISUAL_MODE)) g_canDraw=false;

   string gvName = StringFormat("ORB_BASE_%I64d_%I64d",
                                AccountInfoInteger(ACCOUNT_LOGIN), InpMagic);
   if(InpAccountBaseline>0)
      g_baseline=InpAccountBaseline;
   else if(GlobalVariableCheck(gvName))
      g_baseline=GlobalVariableGet(gvName);
   else
     {
      g_baseline=AccountInfoDouble(ACCOUNT_BALANCE);
      GlobalVariableSet(gvName, g_baseline);
     }

   //--- build R (G1): variabili globali del contatore delle richieste
   g_gvReq    = StringFormat("ORB_REQ_%I64d_%I64d",    AccountInfoInteger(ACCOUNT_LOGIN), InpMagic);
   g_gvReqDay = StringFormat("ORB_REQDAY_%I64d_%I64d", AccountInfoInteger(ACCOUNT_LOGIN), InpMagic);
   GuardNewDay();

   g_initEq      = AccountInfoDouble(ACCOUNT_BALANCE);
   g_peakEq      = g_initEq;
   g_minEq       = g_initEq;
   g_maxRelDDpct = 0;
   g_maxDayLoss  = 0;

   if(CalendarIsDE())
      Print("[ORB] Calendario festivita': XETRA (Germania)");
   else
      Print("[ORB] Calendario festivita': NYSE (USA)");

   //--- build tarata su NAS100/US100: avvisa se il simbolo non combacia
   string symU=_Symbol;
   StringToUpper(symU);
   bool isNas = (StringFind(symU,"NAS")>=0   || StringFind(symU,"US100")>=0 ||
                 StringFind(symU,"USTEC")>=0 || StringFind(symU,"NDX")>=0   ||
                 StringFind(symU,"US_100")>=0);
   if(!isNas)
      PrintFormat("[ORB] *** ATTENZIONE: questa build e' validata su NAS100/US100 ma il simbolo e' %s. Verificare prima di operare. ***", _Symbol);
   if(InpTimeMode==TIME_MANUAL)
     {
      if(CalendarIsDE() && InpManualOpenHour!=10)
         Print("[ORB] *** ATTENZIONE: calendario XETRA ma apertura manuale diversa da 10:00. Verificare InpManualOpenHour/InpSessionMinutes(510). ***");
      if(!CalendarIsDE() && InpManualOpenHour!=16)
         Print("[ORB] *** ATTENZIONE: calendario NYSE ma apertura manuale diversa da 16:30. Verificare InpManualOpenHour/InpSessionMinutes(390). ***");
     }

   LoadNews();

   PrintFormat("[ORB] Init %s | %s %s | orario=%s fuso=%s baseGMT=%d | rischio=%s | stop %.1f%%ATR | RVOL %s>=%.2f | range [%g-%g]%%ATR | parziale %s %.1fR frac=%d | trail %s %.0f%%ATR | baseline %.2f",
               BUILD_ID, _Symbol, EnumToString(InpORTimeframe),
               (InpTimeMode==TIME_AUTO_NY?"AUTO-NY":"MAN"),
               (InpServerTZ==SRV_EU_DST?"EU-DST":"FISSO"), InpServerBaseGMT,
               RiskModeText(),
               InpStopATRPct, (InpUseRVOL?"ON":"off"), InpRVOLThreshold,
               InpRangeMinPctATR, InpRangeMaxPctATR,
               (InpUsePartial?"ON":"off"), InpPartialTriggerR, (int)InpPartialFrac,
               (InpUseTrailing?"ON":"OFF"), InpTrailATRPct, g_baseline);

   PrintFormat("[ORB] Esecuzione: deviation %.2f pt indice = %d punti simbolo (digits %d, point %g) | spread ora %.2f | ATR(D1) %.2f | timer EoD %s",
               InpMaxSlipIndexPts, g_devPoints, _Digits, _Point,
               SpreadIndexPts(), DailyATR(), (InpUseEoDTimer?"ON":"off"));
   PrintFormat("[ORB] Filtro di allineamento: %s", AlignModeText());
   PrintFormat("[ORB][GUARDIA] %s | budget %d richieste al giorno (usate oggi %d) | ingresso: max %d invii, pausa %d s, inseguimento max %.2f pt indice, invio solo se margine richiesto <= %.0f%% del libero | chiusure rifiutate: pausa %d s (%d s se permanente), max %d tentativi al giorno",
               (InpGuardOn ? "ATTIVA" : "SPENTA (trading come la build Q2)"), InpGuardDailyBudget, g_gReqToday,
               GUARD_MAX_ENTRY_SENDS, GUARD_RETRY_PAUSE_SEC, InpMaxSlipIndexPts, GUARD_MARGIN_SAFETY*100.0,
               GUARD_CLOSE_PAUSE_SEC, GUARD_CLOSE_PAUSE_PERM_SEC, GUARD_MAX_CLOSE_SENDS);

   if(InpDryRun)
      Print("[ORB] *** DRY RUN ATTIVO: nessun ordine verra' inviato. ***");
   else if(!TradingIsLive())
      Print("[ORB] Algo Trading non abilitato -> modalita' OSSERVAZIONE: misura lo spread e logga i segnali senza operare.");

   if(InpUseEoDTimer)
      EventSetTimer((int)MathMax(1, InpEoDTimerSec));

   return INIT_SUCCEEDED;
  }

void OnDeinit(const int reason)
  {
   EventKillTimer();
   Comment("");
   if(InpCleanChartOnExit)
      ObjectsDeleteAll(0, "ORB_", -1, -1);
   if(g_hATR!=INVALID_HANDLE)
      IndicatorRelease(g_hATR);
   if(g_hAlignEMA!=INVALID_HANDLE)
      IndicatorRelease(g_hAlignEMA);
   if(g_hAlignSMA!=INVALID_HANDLE)
      IndicatorRelease(g_hAlignSMA);
  }

//=== SICUREZZA FINE SESSIONE (indipendente dai tick) ================
// Nei pre-festivi i tick possono esaurirsi prima del cut: senza questo
// la posizione resterebbe aperta oltre la sessione (era il residuo del
// trade tenuto 32h a Capodanno). Non tocca nient'altro della logica.
void OnTimer()
  {
   if(!InpUseEoDTimer)   return;
   if(g_totalBlocked)    return;
   if(g_sessCloseCut<=0) return;

   //--- ATTENZIONE: TimeCurrent() e' l'ora dell'ULTIMA QUOTAZIONE, quindi
   //    senza tick NON avanza e renderebbe inutile questo blocco.
   //    TimeTradeServer() e' calcolata dal terminale in locale e avanza
   //    sempre. Prendo il massimo delle due per non dipendere da una sola.
   datetime tSrv = TimeTradeServer();
   datetime tTck = TimeCurrent();
   datetime now  = (tSrv>tTck ? tSrv : tTck);

   if(now < g_sessCloseCut) return;
   if(g_eodTries >= 20)     return;   // evita spam a mercato chiuso
   if(!HasPosition())       return;
   g_eodTries++;
   PrintFormat("[ORB] EoD via TIMER (tentativo %d, ora server %s): chiusura indipendente dai tick.",
               g_eodTries, TimeToString(now, TIME_DATE|TIME_MINUTES));
   CloseAll("EoD close (timer)");
  }

//=== TRACKING METRICHE FTMO =========================================
void TrackFTMO()
  {
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   if(eq<=0) return;
   if(g_initEq<=0) g_initEq=eq;
   if(g_peakEq<=0) g_peakEq=eq;
   if(g_minEq <=0) g_minEq =eq;
   if(eq>g_peakEq) g_peakEq=eq;
   if(eq<g_minEq)  g_minEq =eq;
   if(g_peakEq>0)
     {
      double rel=(g_peakEq-eq)/g_peakEq*100.0;
      if(rel>g_maxRelDDpct) g_maxRelDDpct=rel;
     }
   if(g_dailyRefEq>0)
     {
      double dl=g_dailyRefEq-eq;
      if(dl>g_maxDayLoss) g_maxDayLoss=dl;
     }
  }

void OnTick()
  {
   TrackFTMO();
   if(g_totalBlocked)
     {
      UpdatePanel();
      return;
     }

   datetime now=TimeCurrent();
   MqlDateTime t;
   TimeToStruct(now,t);
   int dayId = t.year*10000 + t.mon*100 + t.day;

   if(dayId!=g_lastDayId)
      OnNewDay(dayId, now);

   // stop hit: posizione tracciata sparita senza chiusura nostra
   if(g_trackOpen && !g_selfClosing && !HasPosition())
     {
      g_trackOpen=false;
      g_lastReason="STOP hit";
      DrawStopHit(now, g_curSL);
      PrintFormat("[ORB] STOP HIT | entry %.2f | SL %.2f | %s%s",
                  g_trackEntry, g_curSL, g_trackLong?"LONG":"SHORT",
                  g_beDone?" (dopo BE: perdita ~0)":"");
     }

   CheckGuards();
   if(g_totalBlocked || g_dailyBlocked)
     {
      UpdatePanel();
      return;
     }

   // chiusura pre-news
   CheckNewsClose(now);

   // chiusura fine sessione
   if(HasPosition() && now>=g_sessCloseCut)
      CloseAll("EoD close");

   // gestione posizione aperta (parziale/BE/trailing)
   if(HasPosition())
      ManagePosition(now);

   // finestra ingresso: dopo chiusura candela 1, entro fine candela 2
   int tfSec=PeriodSeconds(InpORTimeframe);
   if(!g_doneToday && !HasPosition() && !g_targetReached &&
      now>=g_sessOpen+tfSec && now<g_entryDeadline)
      TryEnter(now);

   UpdatePanel();
  }

//=== CRITERIO PERSONALIZZATO PER OTTIMIZZAZIONE =====================
// Obiettivo = profitto netto; drawdown e n.trade come soglie di scarto.
// Stampa inoltre le tre metriche FTMO nel Diario del tester.
double OnTester()
  {
   double profit = TesterStatistics(STAT_PROFIT);
   double ddpct  = TesterStatistics(STAT_EQUITYDD_PERCENT);
   double ntr    = TesterStatistics(STAT_TRADES);

   //--- metriche FTMO misurate tick per tick
   double absDD    = (g_initEq>0 ? g_initEq-g_minEq : 0.0);
   if(absDD<0) absDD=0;
   double absDDpct = (g_initEq>0 ? absDD/g_initEq*100.0 : 0.0);
   double dayPct   = (g_initEq>0 ? g_maxDayLoss/g_initEq*100.0 : 0.0);

   Print("========== VERIFICA FTMO ==========");
   PrintFormat("1) PERDITA MAX SOTTO IL DEPOSITO (regola FTMO 10%%): %.2f USD = %.2f%%  -> %s",
               absDD, absDDpct, (absDDpct>=10.0 ? "*** VIOLATO ***" : "ok"));
   PrintFormat("2) PERDITA GIORNALIERA MAX (regola FTMO 5%%): %.2f USD = %.2f%%  -> %s",
               g_maxDayLoss, dayPct, (dayPct>=5.0 ? "*** VIOLATO ***" : "ok"));
   PrintFormat("3) DRAWDOWN PICCO-MINIMO (peggior data di partenza): %.2f%%  -> %s",
               g_maxRelDDpct, (g_maxRelDDpct>11.0 ? "SOPRA soglia 11%" : "entro soglia 11%"));
   PrintFormat("   Profitto %.2f USD = %.1f R (a 300$/R) su %d operazioni",
               profit, profit/300.0, (int)ntr);
   if(g_slipN>0)
      PrintFormat("4) SLIPPAGE INGRESSO: medio %.2f punti prezzo, peggiore %.2f, su %d ordini",
                  g_slipSum/g_slipN, g_slipMax, g_slipN);
   else
      Print("4) SLIPPAGE INGRESSO: nessun dato (esecuzione ideale nel tester)");
   if(g_sprN>0)
      PrintFormat("5) SPREAD ALL'INGRESSO: medio %.2f punti indice, peggiore %.2f, su %d misure",
                  g_sprSum/g_sprN, g_sprMax, g_sprN);
   Print("===================================");

   if(ntr < 150)     return(0.0);   // campione insufficiente: scarta
   if(ddpct > 12.0)  return(0.0);   // fuori vincolo di rischio: scarta
   if(profit <= 0.0) return(0.0);   // in perdita: scarta
   return(profit);                  // obiettivo = profitto netto
  }
//+------------------------------------------------------------------+
