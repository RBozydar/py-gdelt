## Chapter 5

## CAMEO Ethnic Coding Scheme

## 5.1 Introduction

CAMEOECS systematically assigns three-letter (lower-case) alphabetic codes to individual ethnic groups and generalized ethnic terms. It was created in 2011 as a part of a larger, CAMEObased project, and is thus intended to serve as an optional supplement to CAMEO codes. The CAMEOECS directory includes a relatively comprehensive list of 603 ethnic groups; and a slightly less comprehensive list of each ethnic group's primary countries of settlement. CAMEOECS is distinct from CAMEORCS in that (i) religious groups are not treated as ethnic groups by CAMEOECS (unless there is a clear ethnic dimension) and (ii) the group entries within CAMEOECS are nonhierarchical.

The three primary components of CAMEOECS are Ethnic Group Names , Ethnic Group Codes , and Selected Countries. Ethnic Group Names reports the most common English-language name of each ethnic-group entry in CAMEOECS. Ethnic Group Codes provides a unique three-letter (lower case) alphabetic code for each ethnic group entry included within CAMEOECS. Selected Countries lists the primary countries of settlement (by UN Country Code) for each ethnic group included in CAMEOECS. What follows is a more detailed description of each of these three components, as well as a discussion of the coding decisions that were used to create each.

## 5.2 Identification of Ethnic Groups

To create a comprehensive list of ethnic groups, CAMEOECS drew from two primary sources: (1) the International Organization for Standardization's (ISO) Codes for the Representation of Names of Languages (ISO-639.2; http://www.loc.gov/standards/iso639-2/) and (2) the Ethnic Power Relations (EPR) dataset 3.1 (http://www.epr.ucla.edu/). The creation of a CAMEOECS ethnic groups list from these two sources unfolded in the following four steps:

- 1. First, the subset of all ISO 639.2 Languages that corresponded to specific ethnic groups were identified, and this list was then used as the baseline-set of ethnic groups for inclusion in CAMEOECS.
- 2. ISO 639.2 Languages that did not correspond to a specific ethnic group were discarded. Examples of ISO 639.2 Languages that were discarded include language-entries that were determined to be extinct (e.g. "Phoenician"), artificial (e.g. "Klingon") or representative of general language families that encompassed multiple ethnic groups (e.g. "Baltic languages").

- 3. The ethnic groups included in the EPR 3.1 dataset were then matched by hand to the verified, ISO-639.2-derived baseline-set of ethnic group (described in step one).
- 4. After this matching exercise was completed, roughly 200 additional ethnic groups were found to uniquely exist within the EPR 3.1 dataset, and these groups were then added to the matched CAMEOECS ethnic group list to create the final CAMEOECS list of ethnic groups.

Altogether, this coding scheme identified 603 unique ethnic groups.

## 5.3 CAMEOECS Components

## 5.3.1 Ethnic Group Names

Each CAMEOECS ethnic group identified through the process described above was then assigned a unique Ethnic Group Name for identification and referencing purposes. These Ethnic Group Names , which appear in Table 5.1 below (column one), report the primary English name of each CAMEOECS ethnic group entry. An ethnic group's "primary" name is defined as that group's most commonly used name within modern (spoken) English. In order to systematically determine each ethnic group's most common (spoken) English name, an ethnic group's default Wikipedia (http://www.wikipedia.org/ ) name entry was used as its primary Ethnic Group Name . As a result, many of the Ethnic Group Names that are used in Table 5.1 differ from the names given to these "groups" by ISO 639.2 (which instead lists the "English Name of Language" corresponding to each groups) or by the EPR 3.1. Where applicable, alternative (English-language) ethnic group names-based largely on the EPR 3.1's ethnic group name(s)-appear in parentheses after the primary Ethnic Group Name in Table 5.1 (column one). Note however that these alternative spoken-English Ethnic Group Names are by no means comprehensive. Lastly, in instances where more than one ethnic group was found to use the same primary Ethnic Group Name , groups are distinguished by the inclusion of their region of settlement within their Ethnic Group Name .

## 5.3.2 Ethnic Group Codes

In addition to an Ethnic Group Name , each ethnic group entry in Table 5.1 was assigned a unique three-letter (lower case) alphabetic actor-code (column 2), hereafter referred to as Ethnic Group Code . Ethnic groups were assigned unique Ethnic Group Codes based either on (i) an ethnic group's three letter (lower case) ISO 639.2 Language code (in cases where ethnic groups were found to have a matching ISO 639.2 Language in Step 1 of section 5.2 above) or-in instances where ethnic groups did not have a matching ISO 639.2 Language code-(ii) a mnemonically assigned three letter-code derived from that group's Ethnic Group Name . Regarding case (i), several ISO 639.2 Languages have two unique ISO 639.2 Language code entries-one for bibliographic purposes and one for terminology purposes-and in these instances the bibliographic ISO 639.2 codes were used for Ethnic Group Name . Regarding case (ii), care was taken to ensure that the mnemonically assigned Ethnic Group Codes did not conflict with any existing ISO 639.2 Language codes; including the ISO 639.2 codes for ISO 639.2 Language entries that were discarded in Step 2 of section 5.2 above (i.e. extinct, overly general, or artificial ISO 639.2 Languages). Note that as a result of this latter consideration, some ethnic groups were assigned mnemonic Ethnic Group Codes that were not the "ideal" mnemonic abbreviations of their corresponding Ethnic Group Name . In sum, the Ethnic Group Codes in Table 5.1 perfectly correspond to ISO 639.2 Language codes in instances where CAMEOECS ethnic groups have matching ISO 639.2 Languages, and distinctly correspond to newly

created, mnemonic codes in instances where CAMEECS ethnic groups did not have existing ISO 639.2 Language entries.

## 5.3.3 Selected Countries

Selected Countries reports the primary countries of settlement for each ethnic group entry in Table 5.1. A "country of settlement" is defined as any country where an ethnic group is deemed to be politically relevant (based on the EPR 3.1's definition of political relevancy) or have a sizable population (roughly greater than 1,000 ethnic group members). 1 Selected Countries are listed in Table 5.1 by (comma-separated, alphabetized) United Nations Country Codes (as defined in Table 9.1), and were collected from two primary sources.

First, all of an ethnic group's countries of relevance (for years 1946-2005) were identified within the EPR 3.1. If a country was indicated as being a relevant for a given ethnic groupfor any year within the EPR 3.1's 1946-2005 sample frame -it was added as a Selected Country for that ethnic group's entry in Table 5.1 below. While the EPR 3.1 deems some countries to be relevant to specific ethnic groups in some years but not others, the goal of CAMEOECS is to capture every country where an ethnic group could potentially be active, and therefore the EPR 3.1's year/relevance constraints were not applied to a given ethnic group's Selected Country listings below. Note that not all ethnic groups included within CAMEOECS had a matching EPR 3.1 entry, and accordingly, the use of EPR 3.1 countries of relevance in coding Selected Countries applies to some CAMEOECS ethnic groups but not others.

Second, ethnic groups' Wikipedia entries were used to assess these groups' "regions of significant populations." Where these regions were listed with specific population numbers, any country with greater than 1,000 members of a given ethnic group was included as a Selected Country for that ethnic group in Table 5.1. Note that this coding scheme has a moderate bias towards large developed countries with significant histories of immigration (e.g. Australia, France, the United States of America). For Wikipedia entries that did not report specific population numbers, or that did not contain a "regions of significant populations" section at all, any country included on that ethnic group's Wikipedia page was added as a Selected Country for that group. Note that, irrespective of whether a given ethnic group had a "regions of significant populations" section or not, Wikipedia entries for ethnic groups were often incomplete and are thus likely missing many countries with significant populations of CAMEOECS ethnic groups. Selected Country is therefore very much a work-in-progress. Also note that the use of ethnic groups' Wikipedia page entries to code Selected Countries was applied both to groups that had no relevant-country entries in the EPR 3.1 and to ethnic groups with relevant countries listed by the EPR 3.1. Regarding the latter, there was often a high degree of correspondence between the countries listed under Wikipedia and those included in the EPR 3.1. However, when additional countries were listed in one source but not the other, these additional countries were always included within Selected Countries , so as to create the most compressive list of ethnic groups' countries of settlement as was possible at this time.

$^{1}$According to the EPR 3.1. codebook (pg. 2), “An ethnic category is politically relevant if at least one significant political actor claims to represent the interests of that group in the national political arena, or if members of an ethnic category are systematically and intentionally discriminated against in the domain of public politics. By ‘significant’ political actor we mean a political organization (not necessarily a party) that is active in the national political arena. We define discrimination as political exclusion directly targeted at an ethnic community thus disregarding indirect discrimination based, for example, on educational disadvantage or discrimination in the labor or credit markets.”

Table 5.1: CAMEO Ethnic Group Codes

| Ethnic Group Name                   | Code   | Selected Countries                                                                                 |
|-------------------------------------|--------|----------------------------------------------------------------------------------------------------|
| Abkhaz (Abkhazians)                 | abk    | GEO, DEU, RUS, SYR, TUR, UKR                                                                       |
| Aboriginal-Australians (Aborigines) | abr    | AUS                                                                                                |
| Acehnese (Achinese)                 | ace    | IDN, MYS                                                                                           |
| Achang                              | acg    | CHN, MMR                                                                                           |
| Acholi                              | ach    | SDN, UGA                                                                                           |
| Adivasi                             | adi    | IND, NPL                                                                                           |
| Adjarians (Adzars)                  | adj    | GEO, TUR                                                                                           |
| Adyghe (Circasians)                 | ady    | BGR, DEU, IRQ, ISR, JOR, LBY, NLD, RUS, SYR, TUR, USA                                              |
| Afar                                | aar    | DJI, ERI, ETH                                                                                      |
| Afrikaners                          | afr    | BWA, LSO, MWI, SWZ, ZAF, ZMB, ZWE                                                                  |
| Ahmadis                             | ahm    | BGD, IND, IDN, PAK                                                                                 |
| Ainu                                | ain    | JPN, RUS                                                                                           |
| Aja                                 | aja    | BEN, TGO                                                                                           |
| Akan (Asante)                       | aka    | BEN, BFA, CAN, CIV, FRA, GBR, GHA, JAM, LBR, MLI, NGA, SUR, TGO, USA                               |
| Aku (Creoles)                       | aku    | GMB                                                                                                |
| Albanians                           | alb    | ALB, CAN, CHE, DEU, DNK, GBR, GRC, HRV, ITA, MKD, MTN, NLD, NOR, ROM, SRB, SWE, TUR, UKR, USA      |
| Aleut                               | ale    | RUS, USA                                                                                           |
| Algonquian                          | alg    | USA                                                                                                |
| Altay (Altai)                       | alt    | RUS                                                                                                |
| Alur                                | alu    | COD, UGA                                                                                           |
| Ambonese (Amboinese)                | amb    | IDN                                                                                                |
| Americo-Liberians                   | ame    | LBR                                                                                                |
| Amhara                              | amh    | CAN, DJI, EGY, ERI, ETH, ISR, NOR, SDN, SOM, SWE, USA, YEM                                         |
| Angika speakers                     | anp    | IND, NPL                                                                                           |
| Ankole                              | nyn    | UGA                                                                                                |
| Apache                              | apa    | USA                                                                                                |
| Arab                                | ara    | DZA, EGY, ISR, IRN, IRQ, JOR, KWT, LBN, LBY, MAR, MLI, SAU, SDN, SOM, SYR, TCD, TUN, USA, YEM      |
| Aragonese                           | arg    | ESP                                                                                                |
| Arapaho                             | arp    | USA                                                                                                |
| Arawak                              | arw    | COL, GUY, SUR, VEN                                                                                 |
| Argentinians                        | atg    | ARG, AUS, BOL, BRA, CAN, CHE, CHL, DEU, ESP, FRA, GBR, ISR, ITA, JPN, MEX, PER, PRY, URY, USA, VEN |

continued on next page

| Ethnic Group Name        | Code   | Selected Countries                                                                      |
|--------------------------|--------|-----------------------------------------------------------------------------------------|
| Armenian                 | arm    | ARG, ARM, AUS, AZE, BRA, CAN, CYP, FRA, GEO, GRC, RN, LBN, POL, RUS, SYR, TUR, UKR, USA |
| Aromanians               | rup    | ALB, BGR, GRC, MKD, ROM, SRB                                                            |
| Ashanti                  | tw     | CIV, GHA                                                                                |
| Asian                    | asa    | AUS, CHN, GBR, JPN, KOR, LAO, MMR, PRK, THA, UGA, USA, VNM, ZAF                         |
| Assamese                 | asm    | IND                                                                                     |
| Assyrian                 | asy    | AUS, BEL, CAN, CHE, DEU, DNK, FRA, IRN, IRQ, ITA, JOR, LBN, NLD, RUS, SWE, TUR, USA     |
| Asturian                 | ast    | ESP                                                                                     |
| Atacamenos               | ata    | CHL                                                                                     |
| Athabaskan               | ath    | CAN, USA                                                                                |
| Australians              | aus    | AUS                                                                                     |
| Austrians                | auu    | AUS, AUT, ARG, CAN, CHE, CZE, DEU, GBR, GRC, HUN, ITA, NZL, SWE, USA, ZAF               |
| Awadhi                   | aw     | IND                                                                                     |
| Aymara                   | aym    | BOL, CHL, PER                                                                           |
| Azande (Azande-Mangbetu) | znd    | CAF, COD, SDN                                                                           |
| Azerbaijani (Azeri)      | aze    | AUT, AZE, BLR, CAN, DEU, GBR, IRN, KAZ, KGZ, LVA, NLD, RUS, TUR, UKR, USA, UZB          |
| Baganda                  | bad    | CAN, GBR, SWE, UGA, ZAF, USA                                                            |
| Bai                      | bii    | CHN                                                                                     |
| Bakongo                  | bkn    | AGO, COD, COG                                                                           |
| Bakweri                  | bkw    | CMR                                                                                     |
| Balanta                  | bln    | GMB, GNB, SEN                                                                           |
| Balinese                 | ban    | IDN                                                                                     |
| Balkars                  | blk    | KAZ, RUS                                                                                |
| Baloch (Baluchis)        | bal    | AFG, ARE, IRN, OMN, PAK                                                                 |
| Bamar (Barman)           | bm     | AUS, GBR, MMR, THA, SGP, MYS, GBR, AUS, USA                                             |
| Bambara                  | bam    | BFA, GIN, MLI, NER, SEN                                                                 |
| Bamileke                 | bai    | CMR                                                                                     |
| Bantu                    | bnt    | AGO, CMR, COD, NAM, TZA, ZAF, ZMB                                                       |
| Banyarwanda              | bny    | COD, UGA                                                                                |
| Bari                     | bar    | SDN                                                                                     |
| Bariba                   | brb    | BEN                                                                                     |
| Bashkirs                 | bak    | BLR, KAZ, KGZ, RUS, TJK, UKR, UZB                                                       |
| Basoga (Bassa/Duala)     | bas    | CMR, UGA                                                                                |
| Basque                   | bq     | ARG, CHL, CRI, CUB, BOL, BRA, ESP, FRA, MEX, URY, USA, VEN                              |

continued on next page

| Ethnic Group Name           | Code   | Selected Countries                                                                                                |
|-----------------------------|--------|-------------------------------------------------------------------------------------------------------------------|
| Baster                      | bst    | NAM                                                                                                               |
| Batak                       | btk    | IDN                                                                                                               |
| Bateke                      | bke    | COD, COG, GAB                                                                                                     |
| Beja                        | bej    | EGY, ERI, SDN                                                                                                     |
| Belarusians (Byelorussians) | bel    | ARG, BEL, BLR, BRA, CAN, EST, GBR, ISR, KAZ, LTU, LVA, MDA, POL, RUS, UKR, USA                                    |
| Bemba                       | bem    | ZMB                                                                                                               |
| Bengali-Hindu (Bengali)     | ben    | BGD, GBR, IND, NPL, MMR, MYS, PAK, SWE, THA, USA                                                                  |
| Beni-Shugal-Gumez           | bni    | ETH                                                                                                               |
| Berber                      | ber    | CAN, DZA, EGY, LBY, MAR, MLI, NER, TUN, USA                                                                       |
| Beti-Pahuin (Beti)          | bte    | CMR, COG, GAB, GNQ, STP                                                                                           |
| Beydan (White Moors)        | bey    | DZA, LBY, MRT, MAR, TUN                                                                                           |
| Bhojpuri                    | bho    | FJI, GUY, IND, MUS, NPL, SUR, TTO                                                                                 |
| Bicolano                    | bik    | PHL                                                                                                               |
| Bihari                      | bih    | BGD, FJI, GBR, GUY, IND, MUS, NPL, PAK, SUR, TTO, USA                                                             |
| Bilen                       | byn    | ERI                                                                                                               |
| Black-African (Africans)    | afa    | BRA, COL, CRI, CUB, DZA, ECU, GBR, HTI, LBY, MEX, MLI, MRT, NIC, PER, TTO, USA, VEN, ZAF, ZWE                     |
| Blang                       | blg    | CHN, MMR, THA                                                                                                     |
| Bodo                        | bod    | IND                                                                                                               |
| Bolivia                     | bol    | BOL, CHL, PER, PRY                                                                                                |
| Bonan                       | bon    | CHN                                                                                                               |
| Bosniaks                    | bos    | AUS, AUT, BEL, BIH, DEU, DNK, HRV, ITA, MKD, MTN, NOR, SRB, SVN, SWE, TUR, USA                                    |
| Brahui                      | brh    | AFG, IRN, PAK                                                                                                     |
| Breton                      | bre    | CAN, FRA                                                                                                          |
| Brijwasi                    | bra    | IND                                                                                                               |
| Bugis                       | bug    | IDN, MYS, SGP                                                                                                     |
| Bulgarian                   | bul    | ALB, ARE, AUT, BEL, BGR, CAN, CZE, DEU, ESP, FRA, GBR, GRC, HUN, ITA, KAZ, MDA, PRT, ROM, RUS, SRB, TUR, UKR, ZAF |
| Burakumin                   | brk    | JPN                                                                                                               |
| Buryat                      | bua    | KAZ, MNG, RUS, UZB, UKR                                                                                           |
| Bushmen (San)               | bsh    | BWA, NAM, ZAF                                                                                                     |
| Buyei                       | bou    | CHN, VNM                                                                                                          |
| Cabindan-Mayombe            | cab    | AGO                                                                                                               |
| Caddo                       | cad    | USA                                                                                                               |
| Cape Verdean                | cap    | CPV, GNB                                                                                                          |

continued on next page

| Ethnic Group Name          | Code   | Selected Countries                                                                                                          |
|----------------------------|--------|-----------------------------------------------------------------------------------------------------------------------------|
| Catalan                    | cat    | AND, ARG, CHL, CUB, DEU, ESP, FRA, ITA, MEX, VEN                                                                            |
| Caucasian Avars (Avars)    | ava    | AZE, GEO, RUS                                                                                                               |
| Cebuano                    | ceb    | PHL                                                                                                                         |
| Chagatai                   | chg    | UZB                                                                                                                         |
| Cham                       | cmc    | FRA, KHM, LAO, MYS, THA, USA, VNM                                                                                           |
| Chamorro                   | cha    | FSM, MNP, USA                                                                                                               |
| Chechen                    | che    | AZE, EGY, GEO, IRN, IRQ, JOR, KAZ, RUS, SYR, TUR                                                                            |
| Cherokee                   | chr    | USA                                                                                                                         |
| Chewa                      | chw    | MWI                                                                                                                         |
| Chewa (Nyanja speakers)    | nya    | MOZ, MWI, ZMB, ZWE                                                                                                          |
| Cheyenne                   | chy    | USA                                                                                                                         |
| Chileans                   | chl    | ARG, BRA, CHL, DEU, ESP, FRA, SWE, USA, VEN                                                                                 |
| Chinese (Mainland Chinese) | chi    | AUS, BRA, CAN, CHN, ESP, FRA, GBR, IDN, IND, ITA, KHM, KOR, LAO, MMR, MYS, NLD, NZL, PER, PHL, PRK, SGP, THA, USA, VNM, ZAF |
| Chinook                    | chn    | USA                                                                                                                         |
| Chipewyan                  | chp    | CAN                                                                                                                         |
| Choctaw                    | cho    | USA                                                                                                                         |
| Ch'orti' (Chorti)          | cht    | GTM, HND                                                                                                                    |
| Chukchi                    | chc    | RUS                                                                                                                         |
| Chuukese                   | chk    | FSM                                                                                                                         |
| Chuvash                    | chv    | BLR, KAZ, KGZ, MDA, RUS, TKM, UZB                                                                                           |
| Colombian                  | col    | ARG, AUS, BRA, CAN, COL, CRI, ESP, GBR, ISR, ITA, MEX, USA, VEN                                                             |
| Cook Islands Maori         | rar    | COK, NZL                                                                                                                    |
| Cornish                    | cor    | AUS, CAN, GBR, MEX, NZL, USA, ZAF                                                                                           |
| Corsican                   | cos    | FRA                                                                                                                         |
| Costa Ricans               | csr    | CRI, NIC, PAN                                                                                                               |
| Cotiers                    | cot    | MDG                                                                                                                         |
| Cree                       | cre    | CAN, USA                                                                                                                    |
| Creole                     | crp    | BLZ, CPV, DMA, GLP, GMB, GNB, GNO, HTI, JAM, LCA, MTO, NGA, SEN, SLE, STP, TTO                                              |
| Crimean Tatar              | crh    | BGR, ROM, TUR, UKR, UZB                                                                                                     |
| Croats                     | hrv    | ARG, AUS, AUT, BIH, CAN, CHE, CHL, DEU, DNK, FRA, HRV, HUN, ITA, MTN, NOR, ROM, SRB, SVN, SWE, USA, ZAF                     |
| Cushitic                   | cus    | EGY, KEN, SDN, SOM, TZA                                                                                                     |

continued on next page

| Ethnic Group Name               | Code   | Selected Countries                                                                                                                    |
|---------------------------------|--------|---------------------------------------------------------------------------------------------------------------------------------------|
| Czech                           | cze    | ARG, AUS, AUT, BRA, CAN, CHE, CZE, DEU, ESP, FRA, GBR, HRV, ISR, IRL, ITA, MEX, NLD, POL, ROM, RUS, SRB, SVK, SVN, SWE, UKR, USA, ZAF |
| Dai                             | dai    | CHN, LAO, THA                                                                                                                         |
| Dalit (Backward classes/castes) | dal    | BGD, IND, LKA, NPL, PAK                                                                                                               |
| Damara                          | dam    | NAM                                                                                                                                   |
| Danes                           | dan    | AUS, AUT, BRA, CAN, CHE, DEU, DNK, ESP, FRA, GBR, IRL, ISL, NOR, NZL, SWE, USA                                                        |
| Dargwa (Dargins)                | dar    | RUS                                                                                                                                   |
| Daur                            | dau    | CHN                                                                                                                                   |
| Dayak                           | day    | BRN, IDN, MYS                                                                                                                         |
| Dinka                           | din    | SDN                                                                                                                                   |
| Djerma-Songhai                  | dje    | NER                                                                                                                                   |
| Dogras                          | doi    | IND, PAK                                                                                                                              |
| Dogrib                          | dgr    | CAN                                                                                                                                   |
| Dominicans                      | dom    | DOM, HTI, USA                                                                                                                         |
| Dong                            | don    | CHN, VNM                                                                                                                              |
| Dongxiang                       | dox    | CHN                                                                                                                                   |
| Dravidian                       | dra    | IND, LKA, PAK                                                                                                                         |
| Druze                           | dru    | AUS, CAN, ISR, JOR, LBN, SYR, USA, VEN                                                                                                |
| Duala                           | dua    | CMR                                                                                                                                   |
| Dutch (Flemings)                | dut    | AUS, CAN, BEL, BRA, NLD, NZL, USA, ZAF                                                                                                |
| Dyula                           | dyu    | BFA, GNB, MLI, SEN                                                                                                                    |
| East Indian                     | ein    | MYS, TTO                                                                                                                              |
| East Timorese                   | eat    | IDN, TMP                                                                                                                              |
| Ecuadorians                     | ecu    | CHL, COL, ECU, ESP, PER, PRY, USA, VEN                                                                                                |
| Edo                             | bin    | NGA                                                                                                                                   |
| Efik                            | efi    | CMR, NGA                                                                                                                              |
| Ekajuk                          | eka    | NGA                                                                                                                                   |
| English                         | eng    | CAN, GBR, IRL, NZL, ZAF                                                                                                               |
| English-Creole                  | cpe    | BLZ, JAM, NGA, SLE                                                                                                                    |
| Eshira (Bapounou)               | esh    | GAB                                                                                                                                   |
| Estonian                        | est    | BEL, CAN, EST, FIN, GBR, IRL, LVA, NOR, RUS, SWE, UKR, USA                                                                            |
| Europeans                       | eur    | ZWE                                                                                                                                   |
| Evenks                          | eve    | CHN, RUS                                                                                                                              |
| Ewe                             | ewe    | BEN, GHA, TGO                                                                                                                         |
| Ewondo                          | ewo    | CMR                                                                                                                                   |
| Fang (Estuary Fang)             | fan    | COG, GAB, GNQ                                                                                                                         |
| Fante                           | fat    | GHA                                                                                                                                   |
| Faroese                         | fao    | DNK, ISL, NOR                                                                                                                         |

| Ethnic Group Name          | Code   | Selected Countries                                                                                                                    |
|----------------------------|--------|---------------------------------------------------------------------------------------------------------------------------------------|
| Fijian                     | fij    | AUS, FJI, GBR, NZL, USA                                                                                                               |
| Filipino                   | fil    | ARE, AUS, CAN, CHN, ESP, ISR, ITA, JPN, KOR, KWT, MYS, NGA, NLD, NOR, NZL, PAK, PHL, QAT, SAU, USA                                    |
| Finno-Ugric                | fiu    | CAN, EST, FIN, HUN, NZL, ROM, RUS, SVK, SWE, USA                                                                                      |
| Finns                      | fin    | ARE, AUS, CAN, CHE, DEU, DNK, ESP, EST, FIN, FRA, NLD, NOR, RUS, SWE, USA                                                             |
| Fon                        | fon    | BEN, NGA                                                                                                                              |
| French                     | fre    | BEL, BRA, CAN, CHE, FRA, GBR, USA                                                                                                     |
| French-Creole              | cpf    | DMA, GLP, HTI, LCA, MTQ, TTO                                                                                                          |
| Frisians                   | frr    | DEU                                                                                                                                   |
| Friulan                    | fur    | ITA                                                                                                                                   |
| Fula (Fulani)              | ful    | BEN, BFA, CAF, CIV, CMR, GIN, GMB, GNB, LBR, MRT, NER, NGA, SDN, SEN, SLE, TCD, TGO                                                   |
| Fur                        | fru    | SDN                                                                                                                                   |
| Ga (Ga-Adangbe)            | ada    | CAN, DEU, GBR, GHA, TGO, USA                                                                                                          |
| Gaels                      | gla    | GBR, IRL                                                                                                                              |
| Galician                   | glg    | AND, ARG, BRA, CHE, CUB, DEU, ESP, FRA, GBR, MEX, NLD, PRT, URY, USA, VEN                                                             |
| Garifuna (Garifs)          | gar    | BLZ, GTM, HND, NIC                                                                                                                    |
| Gayo                       | gay    | IDN                                                                                                                                   |
| Gbaya (Baya)               | gba    | CAF, CMR, COD, COG                                                                                                                    |
| Gelao (Gelo)               | gel    | CHN                                                                                                                                   |
| Georgian                   | geo    | ARM, AZE, BRA, CAN, FRA, GBR, GEO, GRC, ISR, ITA, KAZ, RUS, SGP, TUR, UKR, USA                                                        |
| German                     | ger    | ARG, AUS, AUT, BEL, BOL, BRA, CAN, CHE, CZE, DEU, DNK, ECU, ESP, FRA, GBR, GRC, HUN, ISR, ITA, KAZ, NAM, NOR, POL, ROM, RUS, URY, ZAF |
| Gia Rai                    | gia    | VNM                                                                                                                                   |
| Gin (Jing)                 | gin    | CHN                                                                                                                                   |
| Gio                        | gio    | CIV, LBR                                                                                                                              |
| Gondi                      | gon    | IND                                                                                                                                   |
| Gorontalonese (Gorontalos) | gor    | IDN                                                                                                                                   |
| Grassfielders              | gra    | CMR                                                                                                                                   |
| Grebo                      | grb    | CIV, LBR                                                                                                                              |
| Greek                      | gre    | ALB, ARG, AUS, BEL, BRA, CAN, CHE, CYP, DEU, FRA, GBR, GER, GRC, KAZ, ROM, RUS, SWE, UKR, USA, UZB                                    |

| Ethnic Group Name     | Code   | Selected Countries                                                                       |
|-----------------------|--------|------------------------------------------------------------------------------------------|
| Guan                  | gun    | GHA                                                                                      |
| Guarani               | grn    | ARG, BOL, BRA, PRY                                                                       |
| Guatemalan            | gua    | BLZ, CRI, GTM, HND, MEX, NIC, USA                                                        |
| Gujarati              | guj    | AUS, CAN, GBR, IND, KEN, MDG, MUS, MWI, MYS, SGP, TTO, TZA, UGA, USA, ZAF                |
| Gwich'in              | gwi    | CAN, USA                                                                                 |
| Hadjerai              | had    | TCD                                                                                      |
| Haida                 | hai    | CAN, USA                                                                                 |
| Haitian               | hat    | DOM, ESP, FRA, HTI, USA                                                                  |
| Hani                  | hni    | CHN, VNM                                                                                 |
| Harari                | har    | ETH                                                                                      |
| Haratin (Black Moors) | hrt    | MRT, MAR                                                                                 |
| Hausa (Hausa-Fulani)  | hau    | BEN, BFA, CIV, CMR, ERI, GHA, NER, NGA, SDN, TCD, TGO                                    |
| Hawaiian              | haw    | USA                                                                                      |
| Hazara                | haz    | AFG, PAK                                                                                 |
| Herero                | her    | AGO, BWA, NAM                                                                            |
| Hiligayon             | hil    | PHL                                                                                      |
| Hill Tribes           | hgh    | MDG, THA                                                                                 |
| Himachali             | him    | IND                                                                                      |
| Hiri Motu             | hmo    | PNG                                                                                      |
| Hmong                 | hman   | AUS, CAN, CHN, DEU, FRA, LAO, THA, USA, VNM                                              |
| Hoa                   | hoa    | VNM                                                                                      |
| Hondurans             | hon    | GTM, HND, MEX, SLV, USA                                                                  |
| Hui                   | hui    | CHN                                                                                      |
| Hungarian             | hun    | BRA, CAN, CHL, CZE, GBR, HRV, HUN, IRL, MKD, ROM, RUS, SRB, SVK, SVN, TUR, UKR, USA      |
| Hupa                  | hup    | USA                                                                                      |
| Hutu                  | hut    | BDI, COD, RWA                                                                            |
| Iban                  | iban   | IDN                                                                                      |
| Icelanders            | ice    | CAN, ISL, NOR, USA                                                                       |
| Igbo                  | ibo    | CMR, GBR, GHA, GNQ, JAM, JPN, NGA, SLE, TTO, USA                                         |
| Ijaw                  | ijo    | NGA                                                                                      |
| Ilocono               | ilo    | PHL, USA                                                                                 |
| Indian                | idn    | ARE, AUS, BHR, CAN, FRA, GBR, GUY, IND, KWT, MMR, MUS, NPL, SGP, OMN, SAU, USA, TTO, ZAF |
| Indigenous            | idg    | PHL, MEX, COL, ECU, LBR, CAN, USA                                                        |
| Indonesian            | ind    | ARE, AUS, CAN, IDN, JPN, KOR, MYS, NLD, PHL, SAU, SGP, SUR, USA                          |
| Ingush                | inh    | KAZ, RUS, TUR                                                                            |
| Inuit                 | iku    | CAN                                                                                      |

| Ethnic Group Name    | Code   | Selected Countries                                                                                                    |
|----------------------|--------|-----------------------------------------------------------------------------------------------------------------------|
| Inupiat              | ipk    | CAN, USA                                                                                                              |
| Iranian              | ira    | ARE, AUS,AUT, CAN, CHE, BHR, DEU, DNK, ESP, FRA, GBR, IRN, ISR, ITA, JPN, KWT, MYS, NLD, NOR, PHL, RUS, TUR, SWE, USA |
| Irish                | gle    | ARG, AUS, CAN, GBR, IRL, MEX                                                                                          |
| Iroquois             | iro    | CAN, USA                                                                                                              |
| Italian              | ita    | AUT, CHE, DEU, ESP, FRA, HRV, ITA, SVN, USA                                                                           |
| Japanese             | jpn    | ARG, AUS, BOL, BRA, CAN, CHL, CHN, DEU, FSM, GBR, IDN, ITA, JPN, KOR, MEX, NZL, PER, PHL, PRY, SGP, THA, USA, VNM     |
| Javanese             | jav    | IDN, MYS, NLD, SUR                                                                                                    |
| Jewish               | jew    | ARG, CAN, ISR, IRN, POL, RUS, USA                                                                                     |
| Jino (Jinuo)         | jin    | CHN                                                                                                                   |
| Jola (Diola)         | jol    | GMB, GNB, SEN                                                                                                         |
| Kabarday (Kabardins) | kbd    | GEO, JOR, RUS, TUR                                                                                                    |
| Kabye (Kabre)        | kby    | TGO                                                                                                                   |
| Kabyle               | kab    | CAN, DZA, FRA, USA                                                                                                    |
| Kachin               | kac    | CHN, IND, MMR                                                                                                         |
| Kadazan              | kad    | MYS                                                                                                                   |
| Kakwa-Nubian         | kak    | UGA                                                                                                                   |
| Kalaallit            | kal    | DNK                                                                                                                   |
| Kali'na              | car    | BRA, GUY, SUR, VEN                                                                                                    |
| Kalmyk               | xal    | CHN, MNG, RUS                                                                                                         |
| Kamba                | kam    | KEN                                                                                                                   |
| Kannada              | kan    | IND                                                                                                                   |
| Kanuri (Kanouri)     | kau    | CMR, NER, NGA, TCD                                                                                                    |
| Kaonde               | kao    | COD, ZMB                                                                                                              |
| Kapampangan          | pan    | CAN, PHL, USA                                                                                                         |
| Karachays (Karachai) | kch    | KAZ, RUS, SYR, TUR, USA                                                                                               |
| Karakalpak           | kaa    | KAZ, RUS, TKM, TUR, UZB                                                                                               |
| Karamojong           | krm    | UGA                                                                                                                   |
| Karelians            | krl    | BLR, EST, FIN, RUS                                                                                                    |
| Karen (Kayin)        | kar    | MMR, THA                                                                                                              |
| Kashmiri             | kas    | GBR, IND, PAK                                                                                                         |
| Kashubian            | csb    | CAN, DEU, POL                                                                                                         |
| Kavango              | kav    | NAM                                                                                                                   |
| Kazakhs              | kaz    | CHN, DEU, IRN, KAZ, KGZ, MNG, RUS, TKM, UKR, UZB                                                                      |
| Khakas               | khk    | RUS                                                                                                                   |
| Khasi                | kha    | IND                                                                                                                   |
| Khmer (Khmer Loei)   | khm    | AUS, BEL, CAN, FRA, KHM, KOR, LAO, MYS, NZL, THA, USA, VNM                                                            |
| Khmu                 | khu    | CHN, LAO, MMR, THA, USA, VNM                                                                                          |

continued on next page

| Ethnic Group Name         | Code   | Selected Countries                                                             |
|---------------------------|--------|--------------------------------------------------------------------------------|
| Khoikhoi                  | khi    | NAM, ZAF                                                                       |
| Kikuyu                    | kik    | KEN                                                                            |
| Kinyarwanda Speakers      | kin    | COD                                                                            |
| Kiribati                  | gil    | FJI, KIR, MHL, NRU, SLB, TUV, VUT                                              |
| Kisii                     | kis    | KEN                                                                            |
| Kokani                    | kok    | IND                                                                            |
| Komi (Komi-Permyaks)      | kom    | RUS                                                                            |
| Kongo (Bakongo)           | kon    | AGO, COD, COG                                                                  |
| Kono                      | kno    | SLE                                                                            |
| Korean                    | kor    | ARG, AUS, BRA, CAN, CHN, DEU,                                                  |
|                           |        | FRA, GBR, IDN, IND, JPN, KAZ, KGZ,                                             |
|                           |        | KHM, KOR, MYS, NZL, PHL, PRK,                                                  |
|                           |        | RUS, SGP, THA, UKR, USA, UZB, VNM                                              |
| Kosraean                  | kos    | FSM                                                                            |
| Kouyou                    | kou    | COG                                                                            |
| Kpelle (Guerze)           | kpe    | GHA, LBR                                                                       |
| Krahn (Guere)             | krh    | LBR                                                                            |
| Kru                       | kro    | CIV, LBR                                                                       |
| Ktunaxa                   | kut    | CAN, USA                                                                       |
| Kumyks                    | kum    | RUS                                                                            |
| Kurd                      | kur    | ARM, AZE, DEU, FRA, GBR, IRN, IRQ,                                             |
| Kurichiya (Hill Barhmins) | brm    | IND, NPL                                                                       |
| Kurukh                    | kru    | BGD, IND                                                                       |
| Kwanyama                  | kua    | AGO, NAM                                                                       |
| Kyrgyz (Kirghis/Kirgiz)   | kir    | CHN, KGZ, RUS, TJK, TUR, UKR, UZB                                              |
| Lahu                      | lhu    | CHN, LAO, MMR, THA, VNM                                                        |
| Lak (Russia)              | lak    | RUS                                                                            |
| Lamba                     | lam    | BEN, TGO                                                                       |
| Lao                       | lao    | CHN, KHM, LAO, MMR, MYS, THA, VNM                                              |
| Lari                      | lar    | COG                                                                            |
| Latinos                   | ltn    | CAN, USA                                                                       |
| Latoka                    | ltk    | SDN                                                                            |
| Latvian                   | lav    | BRA, CAN, DEU, ESP, EST, GBR, IRL, KAZ, LTU, LVA, NOR, NZL, RUS, SWE, UKR, USA |
| Lenape                    | del    | CAN, USA                                                                       |
| Lenca                     | len    | HND, SLV                                                                       |
| Lezgian (Lezgins)         | lez    | AZE, RUS                                                                       |
| Li                        | lii    | CHN                                                                            |
| Limba                     | lba    | CMR, SLE                                                                       |
| Limburgian                | lim    | BEL, DEU, NLD                                                                  |
| Lingala                   | lin    | COD, COG                                                                       |
| Lisu                      | lsu    | CHN, IND, MMR, THA                                                             |

continued on next page

| Ethnic Group Name            | Code   | Selected Countries                                                                                           |
|------------------------------|--------|--------------------------------------------------------------------------------------------------------------|
| Lithuanian                   | lit    | AUT, BLR, BRA, CAN, DEU, ESP, FRA, IRL, ISL, LTU, LVA, POL, RUS, USA, ZAF                                    |
| Lomwe (Nguru)                | lom    | MOZ, MWI                                                                                                     |
| Lovale                       | lov    | AGO, ZAM                                                                                                     |
| Lower Sorbian                | dsb    | DEU                                                                                                          |
| Lozi (Barotse)               | loz    | AGO, BWA, NAM, ZMB                                                                                           |
| Luba-Kasai                   | lua    | COD                                                                                                          |
| Luba-Katanga                 | lub    | COD                                                                                                          |
| Lugbara                      | lgb    | COD, UGA                                                                                                     |
| Luhya                        | luh    | KEN, TZA, UGA                                                                                                |
| Luiseno                      | lui    | USA                                                                                                          |
| Lulua                        | lul    | COD                                                                                                          |
| Lumad                        | mno    | PHL                                                                                                          |
| Lunda                        | lun    | AGO, COD, ZMB                                                                                                |
| Luo                          | luo    | COD, ETH, KEN, SDN, TZA, UGA                                                                                 |
| Lusei                        | lus    | BGD, IND, MMR                                                                                                |
| Luxembourgers                | ltz    | ARG, BEL, BRA, FRA, LUX, USA                                                                                 |
| Maasai                       | mas    | KEN, TZA                                                                                                     |
| Macedonian                   | mac    | ALB, AUS, BEL, BIH, CHE, CZE, DEU, DNK, FRA, GBR, GRC, HRV, HUN, ITA, MKD, NOR, SRB, SVK, SVN, SWE, TUR, USA |
| Madhesi                      | mdh    | NPL                                                                                                          |
| Madi                         | mdi    | SDN, UGA                                                                                                     |
| Madurese (Madura)            | mad    | IDN                                                                                                          |
| Mafwe                        | maf    | IDN, NAM                                                                                                     |
| Magahi                       | mag    | IND                                                                                                          |
| Maithili                     | mai    | IND, NPL                                                                                                     |
| Makassarese                  | mak    | IDN                                                                                                          |
| Makonde (Makonde-Yao)        | mok    | MOZ, TZA                                                                                                     |
| Malagasy                     | mlg    | MDG                                                                                                          |
| Malayalam                    | mal    | AUS, CAN, IND, PAK, SAU, THA, USA, ZAF                                                                       |
| Malays                       | may    | BRN, IDN, MYS, SGP, THA                                                                                      |
| Maldivian                    | div    | MDV                                                                                                          |
| Maltese                      | mlt    | AUS, CAN, GBR, MLT, USA                                                                                      |
| Mananja-Nayanja              | mng    | MWI                                                                                                          |
| Manchu                       | mnc    | CAN, CHN, JPN, PRK, RUS, USA                                                                                 |
| Mandar                       | mdir   | IDN                                                                                                          |
| Mande                        | mnd    | BEN, BFA, CIV, GHA, GIN, GMB, GNB, LBR, MLI, MRT, NER, NGA, SEN, SLE, TCD                                    |
| Mandinka (Mandigo/Mandingue) | man    | BFA, CIV, GIN, GNB, LBR, MLI, MRT, NER, SEN, SLE, TCD                                                        |
| Manipuri                     | mni    | IND                                                                                                          |

continued on next page

| Ethnic Group Name   | Code   | Selected Countries                                               |
|---------------------|--------|------------------------------------------------------------------|
| Manjack (Manjaco)   | mnj    | GMB, GNB, SEN                                                    |
| Mano                | mn     | LBR                                                              |
| Manx                | glv    | GBR, USA                                                         |
| Manyika             | mny    | MOZ, ZWE                                                         |
| Maonan              | mon    | CHN                                                              |
| Maori               | mao    | AUS, CAN, GBR, NZL, USA                                          |
| Mapuche             | arn    | ARG, CHL                                                         |
| Marathi             | mar    | AUS, IND, ISR, MUS, USA                                          |
| Mari                | chm    | RUS                                                              |
| Marshallese         | mah    | MHL, NRU                                                         |
| Marwaris            | mwr    | IND                                                              |
| Maya                | myn    | BLZ, GTM, HND, MEX, SLV                                          |
| Mayangnas           | mya    | HND, NIC                                                         |
| M'Baka              | mbk    | CAF, COD                                                         |
| Mbandja             | mba    | CAF, COD, COG                                                    |
| Mbere (Mbede)       | mbe    | COG, GAB                                                         |
| Mbochi              | mbo    | COG                                                              |
| Mbundu-Mestico      | mbu    | AGO                                                              |
| Mende               | men    | SLE                                                              |
| Mestizo             | mtz    | MEX                                                              |
| Miao                | mia    | CHN, FRA, LAO, THA, VNM                                          |
| Mijikenda           | mij    | KEN, SOM, TZA                                                    |
| Mi'kmaq             | mic    | CAN, USA                                                         |
| Minahasa            | mnh    | IDN                                                              |
| Minangkabau         | min    | IDN, MYS                                                         |
| Mirandese           | mwl    | PRT                                                              |
| Miskito             | msk    | HND, NIC                                                         |
| Mizo                | miz    | BGD, IND, MMR                                                    |
| Mohajirs            | moh    | PAK                                                              |
| Mohawk              | moh    | USA                                                              |
| Mokshas             | mdf    | RUS                                                              |
| Mole-Dagbani        | mld    | GHA                                                              |
| Mon                 | mns    | MMR, THA                                                         |
| Mongo               | lol    | COD                                                              |
| Mongol (Mongolians) | mon    | CHN, CZE, JPN, KOR, MING, RUS                                    |
| Mongour (Tu)        | tuu    | CHN                                                              |
| Montenegrins        | mtn    | ALB, ARG, AUS, BIH, BRA, CAN, HRV,  ITA, MKD, MTN, SRB, SVN, TUR |
| Mordvins (Mordva)   | myv    | RUS                                                              |
| Moro                | mro    | BRN, IDN, MYS, PHL                                               |
| Mossi               | mos    | BFA, CIV, GHA                                                    |
| Mulao               | mlo    | CHN                                                              |
| Mulatto             | mla    | HTI                                                              |
| Munda               | mn     | IND                                                              |
| Muong               | muo    | VNM                                                              |
| Muscogee            | mus    | USA                                                              |

| Ethnic Group Name   | Code   | Selected Countries                                                             |
|---------------------|--------|--------------------------------------------------------------------------------|
| Myene               | mye    | GAB                                                                            |
| Naga                | nag    | IND, MMR                                                                       |
| Nahua               | nah    | MEX                                                                            |
| Nakhi (Naxi)        | nax    | CHN                                                                            |
| Nama                | nam    | BWA, NAM, ZAF                                                                  |
| Native American     | nai    | CAN, USA                                                                       |
| Nauruan             | nau    | NRU                                                                            |
| Navajo              | nav    | USA                                                                            |
| Ndonga              | ndo    | AGO, NAM                                                                       |
| Neapolitan          | nap    | ITA                                                                            |
| Nepali              | nep    | ARE, AUS, BTN, CAN, CHN, GBR, IND, JPN, KOR, MMR, MYS, NPL, PAK, QAT, SAU, USA |
| New Zealanders      | nze    | ARE, AUS, CAN, DEU, FRA, GBR, IRL, JPN, NLD, NZL, USA                          |
| Newars              | new    | BTN, CHN, IND, NPL                                                             |
| Ngalop              | dzo    | BTN, IND                                                                       |
| Ngbandi             | ngn    | CAF, COD, COG                                                                  |
| Ngoni               | ngo    | MWI, TZA, ZMB                                                                  |
| Niari               | nir    | COG                                                                            |
| Niasans             | nia    | IDN                                                                            |
| Nibolek             | nib    | COG                                                                            |
| Nicaraguan          | nca    | CRI, GTM, HND, MEX, PAN, NIC, SLV                                              |
| Niuean              | niu    | NIU                                                                            |
| Nkomi               | nkm    | GAB                                                                            |
| Nogais              | nog    | BGR, KAZ, POL, ROM, RUS, TUR, UKR, UZB                                         |
| North Mbundu        | kmb    | AGO                                                                            |
| Northern Ndebele    | nde    | BWA, ZWE                                                                       |
| Northern Sotho      | nso    | ZAF                                                                            |
| Norwegians          | nor    | AUS, BRA, CAN, GBR, NOR, SWE, USA                                              |
| Nu                  | nuu    | CHN                                                                            |
| Nuba                | nba    | SDN                                                                            |
| Nubian              | nub    | EGY, SDN                                                                       |
| Nuer                | ner    | ETH, SDN                                                                       |
| Nung                | nng    | CHN, VNM                                                                       |
| Nuristani           | nur    | AFG                                                                            |
| Nyakyusa            | nyk    | MWI, TZA                                                                       |
| Nyamwezi            | nym    | TZA                                                                            |
| Nyoro               | nyo    | UGA                                                                            |
| Nzema               | nzi    | CIV, GHA                                                                       |
| Occitanians         | oci    | ESP, FRA, ITA, MCO                                                             |
| Ogoni               | ogo    | NGA                                                                            |
| Ojibwe              | oji    | CAN, USA                                                                       |
| Okinawan            | oki    | JPN                                                                            |

| Ethnic Group Name            | Code   | Selected Countries                                                                                                                              |
|------------------------------|--------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| Orgunu                       | oru    | GAB                                                                                                                                             |
| Oriya                        | ori    | IND                                                                                                                                             |
| Oromo                        | orn    | AUS, CAN, DEU, DJI, EGY, ETH, GBR, KEN, SAU, SOM, USA, YEM                                                                                      |
| Osage                        | osa    | USA                                                                                                                                             |
| Ossetians (Ossetes)          | oss    | AZE, GEO, KAZ, RUS, SYR, TJK, TKM, UKR, UZB                                                                                                     |
| Otomi                        | oto    | MEX                                                                                                                                             |
| Ovambo                       | ova    | AGO, NAM                                                                                                                                        |
| Pacific Islanders            | pac    | FJI, FSM, KIR, NRU, NZL, PLW, USA                                                                                                               |
| Pahari Rajput (Rana/Thakuri) | ra     | IND, NPL                                                                                                                                        |
| Palauan                      | pau    | PLW                                                                                                                                             |
| Palestinian                  | pal    | ARE, AUS, CAN, CHL, COL, DEU, EGY, GBR, ISR, IRQ, JOR, KWT, LBN, MEX, PAK, PER, QAT, SAU, SLV, SWE, SYR, USA, YEM                               |
| Panamanians                  | pnm    | COL, CRI, GTM, HND, NIC, PAN                                                                                                                    |
| Pangasinan                   | pag    | PHL                                                                                                                                             |
| Papel                        | ppl    | GNB                                                                                                                                             |
| Papiamento-Creole            | pap    | ABW, NLD                                                                                                                                        |
| Papuan (Papua)               | paa    | IDN, PNG                                                                                                                                        |
| Paraguayan                   | par    | ARG, BOL, BRA, CHL, ESP, PRY, URY, USA                                                                                                          |
| Pashayi (Pashai)             | psh    | AFG                                                                                                                                             |
| Pashtun                      | pus    | AFG, ARE, CAN, GBR, IND, IRN, MYS, PAK, SGP, USA                                                                                                |
| Pehnpeian                    | pon    | FSM                                                                                                                                             |
| Persian                      | per    | AFG, ARE, AUS, BEL, BHR, CAN, CHN, DEU, FRA, GBR, GRC, IND, IRN, ISR, ITA, JPN, KGZ, KOR, KWT, NOR, OMN, PAK, QAT, RUS, SWE, TJK, TUR, UZB, ZAF |
| Peruvian                     | pru    | BOL, BRA, CHL, ECU, PER, PRY, USA                                                                                                               |
| Poles                        | pol    | AUT, AUS, BLR, CAN, CZE, DEU, ESP, FIN, FRA, GRC, IRL, ISL, ITA, KAZ, LTU, LVA, MDA, NLD, NOR, POL, ROM, RUS, SWE, UKR, USA, ZAF                |
| Pomaks                       | pom    | ALB, BGR, GRC, MKD, TUR                                                                                                                         |
| Portuguese                   | por    | AGO, AUS, BEL, BRA, CAN, CHE, ESP, FRA, GBR, GUY, LUX, MOZ, PRT, USA, VEN, ZAF                                                                  |
| Portuguese-Creole            | cpp    | CPV, GMB, GNB, GNQ, SEN, STP                                                                                                                    |
| Pumi                         | pum    | CHN                                                                                                                                             |
| Punjabi                      | pan    | ARE, CAN, CHN, GBR, IND, MYS, PAK, RUS, SAU, USA, ZAF                                                                                           |
| Puthai (Phuthai)             | phu    | LAO                                                                                                                                             |

continued on next page

| Ethnic Group Name           | Code   | Selected Countries                                                                                                |
|-----------------------------|--------|-------------------------------------------------------------------------------------------------------------------|
| Qiang                       | qia    | CHN                                                                                                               |
| Qizilbash                   | qiz    | AFG, IND, PAK                                                                                                     |
| Quechua                     | que    | ARG, BOL, CHL, COL, ECU, PER                                                                                      |
| Rajasthani                  | raj    | IND                                                                                                               |
| Rakhine (Buddist Arakanese) | bda    | BGD, IND, MMR                                                                                                     |
| Rapa Nui                    | rap    | CHL                                                                                                               |
| Romani (Roma)               | rom    | BGR, BIH, CZE, ESP, FRA, GBR, GRC, HRV, HUN, MKD, POL, ROM, RUS, SVK, TUR                                         |
| Romanian                    | rum    | AUS, AUT, CAN, DEU, ESP, FRA, GBR, GRC, HUN, KAZ, MDA, ROM, RUS, SRB, SWE, UKR, USA                               |
| Romansh                     | roh    | CHE                                                                                                               |
| Rundi                       | run    | BDI                                                                                                               |
| Russian                     | rus    | ARM, AUS, BLR, BRA, CAN, CHN, EST, FIN, GBR, GEO, ISR, ITA, KAZ, KGZ, LTU, LVA, MDA, RUS, TJK, TKM, UKR, USA, UZB |
| Salar                       | slr    | CHN                                                                                                               |
| Salish                      | sal    | CAN, USA                                                                                                          |
| Sami                        | smi    | FIN, NOR, RUS, SWE                                                                                                |
| Samoans                     | smo    | AUS, NZL, USA, WSM                                                                                                |
| Sandawe                     | sad    | TZA                                                                                                               |
| Sango                       | sag    | CAF, COD, TCD                                                                                                     |
| Santals                     | fri    | BGD, BTN, IND, NPL                                                                                                |
| Sara                        | sar    | CAF, TCD                                                                                                          |
| Sardinian                   | srd    | ARG, DEU, ITA, USA                                                                                                |
| Sasak                       | sas    | IDN                                                                                                               |
| Scottish (Scots)            | sco    | ARG, AUS, CAN, CHL, GBR, NZL, USA                                                                                 |
| Selkup                      | sel    | RUS                                                                                                               |
| Sena                        | sen    | MWI                                                                                                               |
| Serbs                       | srp    | ALB, BIH, CHE, DEU, DNK, FRA, GBR, GRC, HRV, HUN, ITA, MKD, MTN, ROM, RUS, SRB, SVN, SWE, TUR, USA                |
| Serer                       | srr    | GMB, MRT, SEN                                                                                                     |
| Shaigiya                    | shy    | SDN                                                                                                               |
| Shan                        | shn    | KHM, MMR, THA                                                                                                     |
| She                         | she    | CHN                                                                                                               |
| Shilluk                     | shl    | SDN                                                                                                               |
| Shona (Ndau)                | sna    | MOZ, ZWE                                                                                                          |
| Sicilian                    | scn    | ITA                                                                                                               |
| Sidama                      | sid    | ETH                                                                                                               |
| Siksikawa                   | bla    | CAN                                                                                                               |
| Sindhi                      | snd    | CHN, IND, PAK                                                                                                     |
| Sinhalese                   | sin    | AUS, CAN, GBR, IND, ITA, LKA, MYS, NZL, SGP, USA                                                                  |

| Ethnic Group Name         | Code   | Selected Countries                                                                            |
|---------------------------|--------|-----------------------------------------------------------------------------------------------|
| Siouan                    | sio    | CAN, USA                                                                                      |
| Sioux                     | dak    | USA                                                                                           |
| Slavic                    | sla    | BIH, BLR, CZE, HRV, MKD, MTN, POL, RUS, SRB, SVK, SVN, UKR                                    |
| Slovaks                   | slo    | AUS, AUT, BEL, CAN, CZE, DEU, FRA, GBR, HRV, HUN, IRL, POL, ROM, SRB, SVK, UKR                |
| Slovenes                  | slv    | ARG, AUT, BEL, BIH, BRA, CAN, CHE, DEU, FRA, HUN, NLD, ITA, SRB, SVN, URY, USA                |
| Somali                    | son    | ARE, CAN, DJI, DNK, ETH, GBR, KEN, SAU, SOM, SWE, USA, YEM                                    |
| Songhai                   | son    | MLI, NER                                                                                      |
| Soninke                   | snk    | GHA, GMB, GNB, MLI, MRT, SEN                                                                  |
| Sorbs                     | wen    | DEU                                                                                           |
| Sotho                     | sot    | LSO, ZAF                                                                                      |
| South Ndebele             | nbl    | ZAF                                                                                           |
| Southern Mbandu           | umb    | AGO                                                                                           |
| Spanish                   | spa    | ARG, AUS, BRA, CHE, CUB, DEU, ESP, FRA, GBR, MEX, PER, URY, VEN                               |
| Sranan Tongo              | srn    | SUR                                                                                           |
| Subiya (Basubia)          | bsu    | BWA, NAM, ZMB                                                                                 |
| Sudanese                  | sat    | IDN, SDN                                                                                      |
| Sui                       | sui    | CHN, VNM                                                                                      |
| Sukama                    | suk    | TZA                                                                                           |
| Susu                      | sus    | GIN, SEN, SLE, MLI                                                                            |
| Swahili                   | swa    | TZA, KEN, MOZ, COM                                                                            |
| Swazi                     | ssw    | LSO, MOZ, SWZ, ZAF                                                                            |
| Swedes                    | swe    | AUS, CAN, DEU, DNK, ESP, FIN, FRA, GBR, ITA, NOR, SWE                                         |
| Swiss French              | swf    | CHE                                                                                           |
| Swiss Germans             | gsw    | AUT, CHE, DEU, ITA                                                                            |
| Swiss Italian             | swt    | CHE                                                                                           |
| Tabasaran                 | tab    | RUS                                                                                           |
| Tagalog                   | tgl    | PHL                                                                                           |
| Tahitian                  | tah    | PYF                                                                                           |
| Tai (Tha/Tai-Lu/Tai-Yuan) | tai    | CHN, LAO, MMR, THA, VNM                                                                       |
| Taiwanese                 | twn    | AUS, CAN, CHN, JPN, KOR, PHL, SGP                                                             |
| Tajik (Pamir Tajiks)      | tgk    | AFG, CAN, CHN, DEU, IRN, KGZ, PAK, QAT, RUS, TJK, UZB, USA                                    |
| Tama                      | tms    | SDN, TCD                                                                                      |
| Tamil                     | tam    | IND, LKA, MYS                                                                                 |
| Tatars                    | tat    | AZE, BLR, CHN, EST, FIN, GEO, KAZ, LTU, LVA, MDA, POL, ROM, RUS, TJK, TKM, TUR, UKR, USA, UZB |
| Tawahka                   | taw    | HND                                                                                           |

continued on next page

| Ethnic Group Name          | Code    | Selected Countries                                                                                                           |
|----------------------------|---------|------------------------------------------------------------------------------------------------------------------------------|
| Tay                        | tay     | VNM                                                                                                                          |
| Telugu                     | tel     | IND                                                                                                                          |
| Temne                      | tem     | SLE                                                                                                                          |
| Terenan                    | ter     | BRA                                                                                                                          |
| Ternate                    | trn     | IDN                                                                                                                          |
| Teso                       | tes     | KEN, UGA                                                                                                                     |
| Tetum                      | tet     | AUS, IDN, PRT, TMP                                                                                                           |
| Thai                       | tha     | AUS, CHN, FRA, JPN, KHM, LAO,                                                                                                |
|                            | Tibetan | MMR, MYS, SGP, THA, VNM, USA                                                                                                 |
| Tigray-Tigrinya (Tigry)    | tir     | BTN, CAN, CHE, CHN, IND, NPL, USA                                                                                            |
| Tigre                      | tig     | DJI, ERI, ETH, ISR, ITA, SDN, YEM                                                                                            |
| Tiv                        | tiv     | CMR, NGA                                                                                                                     |
| Tlingit                    | tli     | CAN, USA                                                                                                                     |
| Tok Pisin                  | tpi     | PNG                                                                                                                          |
| Tokelauan                  | tkl     | TKL                                                                                                                          |
| Tonga (Africa)             | tog     | MOZ, MWI, ZMB                                                                                                                |
| Tonga (Pacific)            | ton     | TON                                                                                                                          |
| Tooro                      | tor     | UGA                                                                                                                          |
| Toubou                     | tou     | LBY, NER, SDN, TCD                                                                                                           |
| Transnistrians             | tra     | MDA, RUS                                                                                                                     |
| Tripuri                    | tri     | BGD, IND                                                                                                                     |
| Tsimshian                  | tsi     | CAN, USA                                                                                                                     |
| Tsonga (Tsonga-Chopi)      | tso     | MOZ, SWZ, ZAF, ZWE                                                                                                           |
| Tswana                     | tsn     | BWA, ZAF                                                                                                                     |
| Tuareg                     | tmh     | BFA, DZA, LBY, MLI, NER                                                                                                      |
| Tujia                      | tuj     | CHN                                                                                                                          |
| Tumbuka                    | tum     | MWI, TZA, ZMB                                                                                                                |
| Tupi (Tupi-Guarani)        | tup     | ARG, BRA, PRY, URY                                                                                                           |
| Turkish (Turks)            | tur     | AUS, AUT, AZE, BEL, BGR, BIH, CAN, CHE, CYP, DEU, DNK, EGY, FRA, GBR, GRC, IRQ, KAZ, LBN, MKD, NLD, ROM, RUS, SAU, SWE, SYR, |
| Turkmen                    | tuk     | AFG, IRN, IRQ, SYR, TKM                                                                                                      |
| Tutsi (Tutsi-Banyamulenge) | tts     | BDI, COD, RWA                                                                                                                |
| Tuvaluans                  | tvl     | TUV                                                                                                                          |
| Tuvans (Tuvinians)         | tyv     | CHN, MNG, RUS                                                                                                                |
| Udmurt                     | udm     | RUS                                                                                                                          |
| Ukranian                   | uk      | ARG, ARM, AZE, BLR, EST, GEO, GRC, ITA, KAZ, KGZ, LTU, LVA, MDA, POL, RUS, UKR, USA                                          |
| Upper Sorbian              | hsb     | DEU                                                                                                                          |
| Urban ni-Vanautu           | bis     | VUT                                                                                                                          |
| Urdu                       | urd     | IND, PAK                                                                                                                     |
| Uyghur (Uighur)            | uig     | CHN, KAZ, KGZ, RUS                                                                                                           |

| Ethnic Group Name   | Code   | Selected Countries                                                                         |
|---------------------|--------|--------------------------------------------------------------------------------------------|
| Uzbeks              | uzb    | AFG, CHN, KGZ, MNG, PAK, RUS,  TKM, TJK, USA, UZB                                          |
| Va (Wa)             | vaa    | CHN, MMR                                                                                   |
| Vai                 | vai    | LBR, SLE                                                                                   |
| Venda               | ven    | ZAF, ZWE                                                                                   |
| Venezuelan          | vnz    | CAN, COL, ESP, GBR, USA, VEN                                                               |
| Vietnamese (Kinh)   | vie    | AUS, CAN, CHN, CZE, FIN, FRA, JPN,  KHM, LAO, MYS, NLD, NOR, PHL,  POL, RUS, THA, USA, VNM |
| Vili                | vil    | COG                                                                                        |
| Votes               | vot    | EST, RUS                                                                                   |
| Wakashan            | wak    | CAN                                                                                        |
| Walloons            | wln    | ARG, BEL, BRA, USA                                                                         |
| Waray               | war    | CAN, DEU, PHL, USA                                                                         |
| Washoe              | was    | USA                                                                                        |
| Welayta             | wal    | ETH                                                                                        |
| Welsh               | wel    | ARG, AUS, CAN, GBR, IRL, NZL, USA                                                          |
| Whites              | whi    | ARG, AUS, BRA, CAN, CHL, CRI, CUB,  DEU, MEX, MLI, NAM, PER, URY, USA                      |
| Wolof               | wol    | GMB, MRT, SEN                                                                              |
| Xhosa               | xho    | ZAF                                                                                        |
| Xibe                | xib    | CHN                                                                                        |
| Xinca               | xnc    | GTM                                                                                        |
| Yakuts              | sah    | CAN, CHN, RUS, UKR, USA                                                                    |
| Yao (Africa)        | yao    | MWI                                                                                        |
| Yao (Asia) (Dao)    | dao    | CHN, LAO, THA, VNM                                                                         |
| Yapese              | yap    | FSM                                                                                        |
| Yi                  | iii    | CHN                                                                                        |
| Yoruba              | yor    | BEN, GHA, NGA, TGO                                                                         |
| Yugur               | yug    | CHN                                                                                        |
| Yupik               | ypk    | RUS, USA                                                                                   |
| Zaghawa             | zag    | SDN, TCD                                                                                   |
| Zaidiyya (Zaydis)   | zay    | SAU, YEM                                                                                   |
| Zapotec             | zap    | MEX                                                                                        |
| Zaza                | zza    | DEU, GEO, KAZ, NLD, TUR                                                                    |
| Zenaga              | zena   | MAR, MRT                                                                                   |
| Zhuang              | zha    | CHN                                                                                        |
| Zomi (Chins)        | zom    | BGD, IND, MMR                                                                              |
| Zulu                | zulu   | ZAF                                                                                        |
| Zuni                | zun    | USA                                                                                        |
