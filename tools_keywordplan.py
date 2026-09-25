import csv, sys
sys.path.insert(0,'.')
from build import TOPICS
SUB = {
"nyt-tag":[("tegltag-pris","tegltag pris"),("eternittag-med-asbest","udskiftning af eternittag med asbest"),("tagpap-pris","tagpap pris pr m2"),("staaltag-pris","ståltag pris"),("skifertag-pris","skifertag pris"),("straatag-pris","stråtag pris"),("undertag","nyt undertag pris"),("tagrender-pris","nye tagrender pris")],
"tagmaling":[("rens-af-tegltag","rens af tegltag"),("male-betontagsten","male betontagsten"),("mos-paa-taget","fjerne mos på taget")],
"algerens":[("algerens-facade","algerens facade"),("algerens-fliser","algerens fliser og terrasse")],
"facaderenovering":[("pudset-facade-pris","pudse facade pris"),("udvendig-efterisolering","udvendig efterisolering pris"),("revner-i-facaden","revner i facaden"),("ny-skalmur","ny skalmur pris")],
"facademaling":[("male-murstenshus","male murstenshus"),("silikatmaling","silikatmaling facade"),("male-traefacade","male træfacade pris")],
"omfugning":[("omfuge-selv","omfuge selv"),("kalkmoertel-eller-cement","kalkmørtel eller cementmørtel"),("fuger-smuldrer","fuger smuldrer")],
"sandblaesning":[("sandblaesning-eller-hoejtryksrens","sandblæsning eller højtryksrens"),("fjerne-maling-fra-mursten","fjerne maling fra mursten")],
"nye-vinduer":[("trae-alu-vinduer-pris","træ alu vinduer pris"),("plastvinduer-pris","plastvinduer pris"),("3-lags-glas","3-lags glas eller 2-lags"),("terrassedoer-pris","ny terrassedør pris"),("ovenlysvinduer-pris","ovenlysvindue pris montering"),("vinduer-besparelse","nye vinduer besparelse"),("vinduer-i-lejlighed","udskiftning af vinduer i lejlighed")],
"glarmester":[("termorude-pris","ny termorude pris"),("punkteret-termorude","punkteret termorude"),("glasvaeg-pris","glasvæg pris")],
"tilbygning":[("tilbygning-20-m2","tilbygning 20 m2 pris"),("overetage","byg ovenpå hus pris"),("bebyggelsesprocent","bebyggelsesprocent"),("byggetilladelse-tilbygning","byggetilladelse til tilbygning"),("kvist-pris","ny kvist pris")],
"udestue":[("udestue-materialer","udestue aluminium eller træ"),("kold-eller-varm-udestue","kold eller varm udestue"),("udestue-byggetilladelse","udestue byggetilladelse")],
"carport-og-garage":[("carport-pris","carport pris"),("garage-pris","garage pris"),("carport-regler","carport regler skel"),("dobbelt-carport","dobbelt carport pris")],
"totalentreprise":[("hovedentreprise-eller-totalentreprise","hovedentreprise eller totalentreprise"),("abt-18","abt 18"),("byggeprogram","byggeprogram skabelon")],
"fundament":[("punktfundament","punktfundament til terrasse"),("saetningsskader","sætningsskader"),("understoebning","understøbning pris")],
"nedrivning":[("indvendig-nedrivning","indvendig nedrivning pris"),("fjerne-baerende-vaeg","fjerne bærende væg pris"),("nedrivningstilladelse","nedrivningstilladelse")],
"gulvarbejde":[("gulvafslibning-pris","gulvafslibning pris"),("plankegulv-pris","nyt plankegulv pris"),("gulvvarme-pris","gulvvarme pris"),("klinker-pris","lægning af klinker pris")],
"varmepumpe-luft-til-vand":[("udskift-oliefyr","udskiftning af oliefyr til varmepumpe"),("udskift-gasfyr","udskiftning af gasfyr til varmepumpe"),("stoej-fra-varmepumpe","støj fra varmepumpe regler"),("elforbrug","luft til vand varmepumpe elforbrug"),("radiatorer","varmepumpe og radiatorer")],
"varmepumpe-luft-til-luft":[("multisplit","multisplit varmepumpe pris"),("sommerhus","varmepumpe til sommerhus"),("koeling","varmepumpe med køling")],
"jordvarme":[("jordvarme-besparelse","jordvarme besparelse"),("jordvarme-boring","jordvarme boring pris"),("jordslange","jordslange eller boring")],
"solceller":[("solceller-stoerrelse","hvor mange solceller skal jeg have"),("tilbagebetaling","solceller tilbagebetalingstid"),("solceller-batteri","solceller med batteri"),("solceller-regler","solceller regler og tilladelse"),("solceller-sommerhus","solceller sommerhus")],
"isolering":[("efterisolering-besparelse","efterisolering besparelse"),("isolering-af-kaelder","isolering af kælder"),("isolering-af-gulv","isolering af gulv"),("krybekaelder","krybekælder fugt")],
"loftisolering":[("dampspaerre","dampspærre på loftet"),("papiruld","indblæsning af papiruld"),("skraavaeg","isolering af skråvægge")],
"hulmursisolering":[("materialer","granulat eller papiruld i hulmur"),("problemer","hulmursisolering problemer")],
"energimaerke":[("energimaerke-skala","energimærke skala a til g"),("energimaerke-ved-salg","energimærke ved salg"),("forbedre-energimaerke","forbedre energimærke")],
"badevaerelse-renovering":[("lille-badevaerelse","lille badeværelse pris"),("vaadrumsmembran","vådrumsmembran"),("gulvvarme-i-badevaerelse","gulvvarme i badeværelse"),("walk-in-bruser","walk-in bruser pris"),("badevaerelse-i-lejlighed","nyt badeværelse i lejlighed"),("fliser-pris","flisearbejde badeværelse pris")],
"vvs":[("blandingsbatteri","skift blandingsbatteri pris"),("nyt-toilet","nyt toilet pris med montering"),("varmtvandsbeholder","ny varmtvandsbeholder pris"),("vandroer","udskiftning af vandrør")],
"kloakrenovering":[("hvem-ejer-kloakken","hvem ejer kloakken stikledning"),("rotter-i-kloakken","rotter i kloakken"),("separatkloakering","separatkloakering"),("kloak-stopper","kloak stopper")],
"stroempeforing":[("stroempeforing-eller-opgravning","strømpeforing eller opgravning"),("holdbarhed","strømpeforing holdbarhed")],
"tv-inspektion-kloak":[("kloakrapport","kloakrapport forklaring"),("husekoeb","kloakinspektion ved huskøb")],
"omfangsdraen":[("omfangsdraen-selv","lægge omfangsdræn selv"),("fugt-i-kaelder","fugt i kælder"),("draen-regler","dræn regler")],
"faskine":[("faskine-lerjord","faskine i lerjord"),("faskine-krav","faskine krav og afstand"),("regnvandsopsamling","regnvandsopsamling")],
"vandskade":[("vandskade-forsikring","vandskade forsikring"),("affugtning","affugtning efter vandskade"),("vandskade-lejlighed","vandskade i lejlighed")],
"skimmelsvamp":[("fjernelse-pris","fjernelse af skimmelsvamp pris"),("skimmelsvamp-test","skimmelsvamp test"),("skimmel-i-badevaerelse","skimmel i badeværelse"),("skimmel-paa-loftet","skimmelsvamp på loftet")],
"asbestsanering":[("asbest-regler","asbest regler privat"),("asbest-test","asbest test"),("asbest-i-gulv","asbest i gulvbelægning")],
"belaegning":[("ukrudt-i-fliser","ukrudt i fliser"),("indkoersel-pris","ny indkørsel pris"),("terrasse-fliser","terrasse med fliser pris"),("chaussesten","chaussesten pris")],
"anlaegsarbejde":[("jordarbejde-pris","jordarbejde pris"),("terraenregulering","terrænregulering"),("minigraver","minigraver med fører pris")],
"gartner":[("fast-havepleje","fast havepleje pris"),("haveanlaeg-pris","nyt haveanlæg pris"),("haekklipning","hækklipning pris")],
"hegn":[("lamelhegn","lamelhegn pris"),("hegnsloven","hegnsloven"),("stakit","stakit pris"),("raftehegn","raftehegn pris")],
"toemrer":[("nyt-loft","nyt loft pris"),("traeterrasse-pris","træterrasse pris"),("skillevaeg","ny skillevæg pris")],
"murer":[("pudse-vaeg","pudse væg indvendig pris"),("flisearbejde","flisearbejde pris"),("skorsten","nedtagning af skorsten pris")],
"maler":[("male-loft","male loft pris"),("male-lejlighed","male lejlighed pris"),("male-vinduer","male vinduer pris")],
"elektriker":[("spots-i-loft","spots i loft pris"),("ny-eltavle","ny eltavle pris"),("ladestander","ladestander installation pris"),("ekstra-stikkontakt","ny stikkontakt pris")],
"eltjek":[("eltjek-ved-huskoeb","eltjek ved huskøb"),("hfi-relae","hfi relæ udskiftning")],
"handyman":[("tv-paa-vaeg","montering af tv på væg pris"),("smaaopgaver","handyman små opgaver")],
"haandvaerkertilbud":[("sammenlign-tilbud","sammenligne håndværkertilbud"),("ab-forbruger","ab forbruger"),("haandvaerkerfradrag","håndværkerfradrag"),("klage-over-haandvaerker","klage over håndværker")],
"byggetilbud":[("tjekliste","tjekliste til byggetilbud"),("fast-pris-eller-overslag","fast pris eller overslag")],
"bygherreraadgivning":[("bygherreraadgiver-pris","bygherrerådgiver pris"),("byggetilsyn","byggetilsyn privat")],
"byggesagkyndig":[("bygningssagkyndig","byggesagkyndig eller bygningssagkyndig"),("gennemgang-foer-koeb","gennemgang af hus før køb")],
"tilstandsrapport":[("tilstandsrapport-gyldighed","hvor længe gælder en tilstandsrapport"),("karakterer","tilstandsrapport k0 k1 k2 k3"),("elinstallationsrapport","elinstallationsrapport")],
"faldstammerenovering":[("hvad-betyder-det-for-beboerne","faldstammerenovering beboer"),("finansiering","faldstammerenovering finansiering"),("tidsplan","faldstammerenovering tidsplan")],
"renovering-af-opgang":[("male-opgang","male opgang pris"),("belysning-i-opgang","belysning i opgang")],
"doertelefonanlaeg":[("video-doertelefon","video dørtelefon lejlighed"),("adgangskontrol","adgangskontrol brik opgang")],
"vedligeholdelsesplan":[("andelsboligforening","vedligeholdelsesplan andelsboligforening"),("ejerforening","vedligeholdelsesplan ejerforening")],
"altaner":[("fransk-altan","fransk altan pris"),("altan-andelsbolig","altan andelsbolig")],
"ejendomsservice":[("vicevaert-pris","vicevært pris"),("trappevask","trappevask pris"),("snerydning","snerydning pris")],
}
PK={"nyt-tag":"nyt tag pris","nye-vinduer":"nye vinduer pris","varmepumpe-luft-til-vand":"luft til vand varmepumpe pris","badevaerelse-renovering":"nyt badeværelse pris","totalentreprise":"totalentreprise","haandvaerkertilbud":"håndværkertilbud","byggetilbud":"byggetilbud","vedligeholdelsesplan":"vedligeholdelsesplan","bygherreraadgivning":"bygherrerådgivning","vandskade":"vandskade hvad gør man","skimmelsvamp":"skimmelsvamp i huset","faldstammerenovering":"faldstammerenovering pris","renovering-af-opgang":"renovering af opgang","doertelefonanlaeg":"dørtelefonanlæg pris","altaner":"nye altaner pris","faskine":"faskine","tv-inspektion-kloak":"tv inspektion kloak","ejendomsservice":"ejendomsservice","energimaerke":"energimærke pris"}
rows=[]
for slug,name,hub,target,blurb in TOPICS:
    rows.append({"url":f"/{slug}/","type":"hovedguide","emne":name,"soegeord":PK.get(slug,name.lower()+" pris"),"3byggetilbud":target})
    for sub,kw in SUB.get(slug,[]):
        rows.append({"url":f"/{slug}/{sub}/","type":"underguide","emne":name,"soegeord":kw,"3byggetilbud":target})
urls=[r["url"] for r in rows]; kws=[r["soegeord"] for r in rows]
import collections; print([k for k,c in collections.Counter(kws).items() if c>1], [k for k,c in collections.Counter(urls).items() if c>1])
w=csv.DictWriter(open("content/keywordplan.csv","w",encoding="utf-8",newline=""),fieldnames=list(rows[0]))
w.writeheader(); w.writerows(rows)
print(len(rows),"sider i planen")
