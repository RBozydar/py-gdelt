## CAMEO

Conflict and Mediation Event Observations Event and Actor Codebook

Event Data Project Department of Political Science Pennsylvania State University Pond Laboratory University Park, PA 16802

http://eventdata.psu.edu/

Philip A. Schrodt (Project Director):  (+1)814.863.8978

Version: 1.1b3

March 2012

## Contents

## List of Tables

## Acknowledgments

The CAMEO event coding ontology has been developed over a period of more than a decade and has benefitted from substantial contributions by a number of people. At the risk of missing some people, the major contributors have been:

Initial development of verb and actor ontology (2000-2003): Deborah J. Gerner, O'mur Yilmaz, Philip A. Schrodt

Refinements of actor ontology (2004-2007): Dennis Hermrick, Baris Kesgin, Peter Picucci, Joseph Pull, Almas Sayed, Sarah Stacey

Organized Religion (2009-2011): Matthias Heilke

Ethnic Groups (2011): Jay Yonamine, Benjamin Bagozzi

Funding for CAMEO has been provided by the National Science Foundation (SES-0096086, SES0455158, SES-0527564, SES-1004414)

This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.

Latest update: March 16, 2012

## Preface: About This Manual
In the early days of the web, one would frequently encounter pages highlighted with the phrase "Under Construction" along with some icon, at varying levels of cleverness, invoking roadwork, . These have become less frequent since as the norms of the Web evolved, and the community came to collectively recognize that almost every web site is always "Under construction."

As is this manual. The CAMEO system has been a work-in-progress since it began in 2000, and this manual has been an effort to track and codify those efforts, but is now, and always has been, a working document that has been primarily intended to be used internally at the event data projects first at Kansas, and then at Penn State. Nonetheless, it has information that other people have found useful, and given that one of the first things that seems to get lost in coding projects is the manual, making an imperfect manual available seemed to be the better course of action than waiting to write the perfect manual.

Over the years, we have tried to make it more systematic, and in fact parts have gone through extensive re-writes. But other parts-notably a number of the region-specific codes-weren't really finished (or, to an extent, have been superseded) but still contained information we weren't ready to throw out. The original event coding scheme, and the newer religious and ethnic classification schemes are quite systematic; the actor scheme is very uneven, and we are still working on a separate section on agents.

It is what is it.

## Chapter 1

## Introduction

For several decades, two coding frameworks dominated event data research: Charles McClelland's WEIS [8, 9] and the Conflict and Peace Data Bank (COPDAB) developed by Edward Azar [3, 1, 2]. Both were created during the Cold War and assumed a "Westphalian-Clausewitzian" political world in which sovereign states reacted to each other primarily through official diplomacy and military threats. While innovative when first created, these coding systems are not optimal for dealing with contemporary issues such as ethnic conflict, low-intensity violence, organized criminal activity, and multilateral intervention. McClelland [10, pg. 177] viewed WEIS as only a "first phase"; he certainly did not anticipate that it would continue to be used, with only minor modifications, for four decades.

CAMEO was originally intended merely to support an NSF-funded project on the study of interstate conflict mediation. It was also originally intended to be finished in six months of part-time work. It has, instead, developed as a "next generation" coding scheme designed both to correct some of the long-recognized problems in WEIS and COPDAB, but more importantly, designed both for automated coding and for the detailed coding of sub-state actors. The system was used extensively in the DARPA-funded Integrated Conflict Early Warning System (ICEWS) project [11] and proved surprisingly robust in that environment. Additional detail on the development of the system can be found in

- · http://eventdata.psu.edu/papers.dir/ISA08.pdf
- · http://eventdata.psu.edu/papers.dir/Gerner.APSA.02.pdf

A published version is at [15], and a detailed history of the KEDS project can be found in [13] or http://eventdata.psu.edu/utilities.dir/KEDS.History.0611.pdf .

## 1.0.1 Events

Event categories present in WEIS and COPDAB have both conceptual and practical shortcomings. For instance, WEIS has only a single subcategory for "Military engagement" that must encompass everything from a shot fired at a border patrol to the strategic bombing of cities. COPDAB contains just 16 event categories, spanning a conflict-cooperation continuum that many researchers consider inappropriate. Although there have been efforts to create alternative coding systems-most notably Lengs Behavioral Correlates of War (BCOW) [7]-WEIS and COPDAB remain the predominant frameworks in the published literature.

The lock-in of these early coding systems is readily explained by the time consuming nature of human event coding from paper and microfilm sources. Because human coders typically produce

between five and ten events per hour, and a large data set contains tens of thousands of events, experimental recording is simply not feasible. Established protocols for training and maintaining consistency among coders further constrained efforts to improve WEIS and COPDAB once these were institutionalized. As a consequence, endeavors such as Tomlinson's modification of WEIS [16] and the Global Event Data System (GEDS) project extensions of COPDAB [6] produced only marginal changes.

In contrast to human coding, automated coding allows researchers to experiment with alternative coding rules that reflect a particular theoretical perspective or interest in a specific set of issues. The effort involved in implementing a new or modified coding system, once it has been developed, is relatively small because most of the work can be done within the dictionary of verb phrases. In most cases verb phrases can be unambiguously assigned to appropriate new categories, while obscure phrases are either removed or modified. This elimination of questionable phrases itself represents an improvement in the coding system. Even a long series of texts spanning multiple decades can then be recoded in a few minutes. This allows researchers to focus on maximizing the validity of the coding scheme for their particular research program since the automated coding process itself guarantees the reliability of the system. Consequently in the mid-1990s, the Protocol for the Analysis of Nonviolent Direct Action (PANDA) [4] was developed in an initial experiment with the combination of automated coding and a new ontology focused on sub-state actors, followed by the development of the Integrated Data for Events Analysis (IDEA) [5] system, designed as a super-set of several existing ontologies along with innovations such as the use of tertiary (4-digit) event categories and codes for non-human events such as natural disasters.

In the early stages of the KEDS research, we felt it was important to work with an existing framework so that we could directly compare human-coded and machine-coded data [14]. For a variety of reasons, we selected WEIS, which despite some obvious drawbacks was good enough for our initial analyses. However, we eventually decided to abandon WEIS. Several considerations motivated this choice. First and foremost was our long-standing concern regarding numerous ambiguities, overlaps, and gaps within the WEIS framework. In addition, the distribution of events in WEIS is quite irregular and several of the 2-digit cue categories generate almost no events; we hoped we could improve on this. Third, we wanted to eliminate distinctions among actions that, while analytically discrete, could not be consistently and reliably differentiated using existing news source materials. Finally, as indicated above, the Cold War perspective that permeates WEIS makes it an inappropriate tool for studying contemporary international interactions. Consequently, we developed CAMEO, which is specifically designed to code events relevant to the mediation of violent conflict but can also be used for studying other types of international interactions.

Problems encountered with WEIS are exacerbated due to the lack of a fully specified standard codebook. We based our development of coding dictionaries on the version of the WEIS codebook available through the Inter-university Consortium for Political and Social Research (ICPSR) [9] . The section of the codebook dealing with event categories is quite short-about five pages-and provides only limited guidance. Since McClelland never intended that WEIS would become a de facto coding standard, the ICPSR WEIS codebook was meant to be primarily a proof-of-concept.

We initially intended CAMEO to be an extension of WEIS. Consequently, the first phase of the development of CAMEO involved adding cue and subcategories that we found theoretically necessary for the study of mediation and conflict, while keeping most of the WEIS framework intact. The next phase involved looking for examples of each category and writing definitions for the codebook. This process led to the realization that some of the distinctions we wanted to make for theoretical reasons were simply not possible given the nature of the news leads.

For instance, Promise (WEIS 07) is almost indistinguishable from Agree (WEIS 08) unless the word "promise" is used in the sentence. Therefore, we eventually ended up merging the two into

experiment where we looked at a sample of sentences where Tabari had not identified a verb phrase, and this produced a few new candidate phrases, but only a few.

In the long run, it might be possible to re-define the entire CAMEO coding ontology using the standardized WordNet synsets, rather than using the current categories that were developed inductively. This would would again help align the event coding with the larger NLP community, and probably simplify its use in languages other than English.

## 1.0.2 Actors

One of the major changes in the post-Cold War environment has been the emergence of substate actors as major forces in both domestic and international politics. Many have argued that the proliferation of sub-state, non-state, multi-state, and trans-state actors has blurred almost completely the traditional separation of "international" and "comparative" politics. At times these groups exercise coercive force equal to or greater than that of states, whether from within, as in the case of "failed states", or across borders, as with Israel's attempts to control Hizbollah in Lebanon and Hamas in Gaza, or the near irrelevance of borders in many of the conflicts in central and western Africa. Irrespective of the effectiveness of their coercive power, these non-state actors may also be a source of identity that is more important than that of an individual's state-affiliationthe ability of al-Qaeda to attract adherents from across the Islamic world is a good example-or provide examples of strategies that are imitated across borders, as has been seen in the numerous non-violent popular revolutions in Eastern Europe or the more recent "Arab Spring."

Because they were state-centered, WEIS and COPDAB paid relatively little attention to nonstate actors. A small number of long-lived opposition groups that were active in the 1960s such as the Irish Republican Army, the Palestine Liberation Organization, and the National Liberation Front of Vietnam (Viet Cong) were given state-like codes, as were major international organizations such as the United Nations and the International Committee of the Red Cross/Red Crescent. From the perspective of coding, these actors were treated as honorary states. Beyond this small number of special cases, sub- and non-state actors were ignored.

A major breakthrough in the systematic coding of sub-state actors came with the PANDA project [4], which introduced the concept of sub-state "agents"-e.g.media, politicians, labor unionsas part of their standard actor coding. PANDA's primary focus was on contentious politics within states, and consequently needed to distinguish, for example, between police and demonstrators, or between government and opposition political parties.

Unlike PANDA, which coded the entire world, the KEDS project focused specifically on regions that have experienced protracted conflicts. As a consequence, rather than using the PANDA/IDEA of introducing new agent fields, we initially maintained the WEIS/COPDAB convention of using a single "source" and "target" field. However, because the areas we were coding involved quite a few sub-state actors, we eventually developed a series of standard codes that were initially a composite of the WEIS nation-state codes concatenated with PANDA agent codes. Under this system, for example, ISRMIL would be "Israel military", "LIBOPP" would be Liberian opposition parties, "SIEGOV" would be Sierra Leone government and so forth. After realizing that the simple actor-agent model did not accommodate all of the actors we wished to code, we extended this to a more general hierarchical system that was adopted, with modifications, by ICEWS.

Three principles underlie the CAMEO actor coding system. First, codes are composed of one or more three-character elements: In the present system a code can consist of one, two or three of these elements (and therefore three, six, or nine character codes), although this may be extended later. These code elements are classified into a number of broad categories, such as state actors, sub-state actor roles, regions, and ethnic groups.

Second, the codes are interpreted hierarchically: The allowable code in the second element depends on the content of the first element, and the third element depends on the second. This is in contrast to a rectangular coding system, where the second and third elements would always have the same content. The most familiar analogy to a hierarchical coding system is the Library of Congress cataloguing system, where the elements of the catalog number vary-systematically-depending on the nature of the item being catalogued, and consequently may contain very different information despite being part of a single system. The event coding system used in BCOW [7] is another example of a hierarchical scheme in the event data literature.

Third, we are basing our work on standardized codes whenever these are available. This is most obvious in our use of the United Nations nation-state codes (ISO-3166-1 ALPHA 3) ( http://unstats.un.org/unsd/methods/m49/m49alpha.htm ). This contrasts to the Russett-SingerSmall codes [12] used in WEIS, which are specific to the North American quantitative international relations community. We have generally adopted the IDEA agent codes for sub-state actors. We originally used the HURIDOCS ( http://www.huridocs.org/ ) classifications for world religions, but subsequently expanded this to the much more comprehensive and systematic list found in the CAMEO "Religious Classification System." Similarly, we were unable to locate any systematic list of ethnic minority groups, and instead assembled our own from various sources.

Unfortunately, standard codes are generally not available. For example, most IGOs are known by acronyms of varying lengths, so we need to decide how to truncate these to three characters. We spent considerable time trying to determine whether the U.S. government had a standard list of militarized non-state actors; as best we can tell, this does not exist (or at least not in a form we can access), and the situation for ethnic groups is similar.

## Chapter 2

## VERB CODEBOOK

This chapter gives the extended version of the codebook with annotated examples of each code. A condensed version can be found in Chapter 6.

## 2.1 MAKE PUBLIC STATEMENT

| CAMEO       | 010                                                                                                                                                                                                                                                                                                                                                                                                                    |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | Make statement, not specified below                                                                                                                                                                                                                                                                                                                                                                                    |
| Description | All public statements expressed verbally or in action not otherwise specified. This residual category is not coded except when distinctions among 011 to 017 cannot be made. Note that statements are typically subordinate events; events such as comments are coded as mere statements only when they do not further imply appeals, agreements, support, apologies, demands, disapprovals, rejections, threats, etc. |
| Example     | U.S. military chief General Colin Powell said on Wednesday NATO would need to remain strong.                                                                                                                                                                                                                                                                                                                           |
| CAMEO       | 011                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Name        | Decline comment                                                                                                                                                                                                                                                                                                                                                                                                        |
| Description | Explicitly decline or refuse to comment on a situation.                                                                                                                                                                                                                                                                                                                                                                |
| Usage Notes | This event form is a verbal act. The target could be who the source actor declines to make a comment to or about.                                                                                                                                                                                                                                                                                                      |
| Example     | NATO on Monday declined to comment on an estimate that Yugoslav army and special police troops in Kosovo were losing 90 to 100 dead per day in NATO air strikes.                                                                                                                                                                                                                                                       |

| NAME        | 012                                                                                                                                                                                                                                                                                                                                             |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Make pessimistic comment                                                                                                                                                                                                                                                                                                                        |
| Usage Notes | This event form is a verbal act. Only statements with explicit pessimistic components should be coded as 012; otherwise, default to 010.                                                                                                                                                                                                        |
| Example     | Former West Germany Chancellor Willy Brandt said in a radio interview broadcast today he was skeptical over Moscow's will to agree on limiting European-based nuclear weapons. Israeli Prime Minister Ehud Barak said Friday he was very pessimistic about the chances of resuming peace talks with Syria, Israel radio reported.               |
| CAMEO       | 013                                                                                                                                                                                                                                                                                                                                             |
| Name        | Make optimistic comment                                                                                                                                                                                                                                                                                                                         |
| Usage Notes | This event form is a verbal act. Only statements with explicit optimistic components should be coded as 013; otherwise, default to 010.                                                                                                                                                                                                         |
| Example     | Turkish President Turgut Ozal said on Wednesday he was confident that the United States would remove irritants damaging relations between the two NATO allies.                                                                                                                                                                                  |
| CAMEO       | 014                                                                                                                                                                                                                                                                                                                                             |
| Name        | Consider policy option                                                                                                                                                                                                                                                                                                                          |
| Usage Notes | This event form is typically, although not exclusively, a verbal act. There is no limitation on types of policies that could be under consideration. Europe's leading security forum is exploring the possibility of international patrols to monitor the former Yugoslav republic of Macedonia's border with Serbia, its envoy said on Friday. |
| Example     | Malaysia is considering giving money to 20,000 Vietnamese boat people in the country to entice them to return home, foreign minister said on Tuesday.                                                                                                                                                                                           |
| CAMEO       | 015                                                                                                                                                                                                                                                                                                                                             |
| Name        | Acknowledge or claim responsibility                                                                                                                                                                                                                                                                                                             |
| Description | Non-apologetically claim responsibility, admit an error or wrongdoing, or retract a statement without expression of remorse.                                                                                                                                                                                                                    |
| Usage Notes | This event form is a verbal act. Remorseful acknowledgements should be coded as 'Apologize' (055) instead.                                                                                                                                                                                                                                      |
| Example     | A Damascus-based Palestinian guerrilla group claimed responsibility on Saturday for attacks on Israeli troops from Jordan in the past two days.                                                                                                                                                                                                 |

| NAME         | 016                                                                                                                                                                                                                                                                                                                                            |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Discard or deny accusations or charges.                                                                                                                                                                                                                                                                                                        |
| Usage Notes  | This event form is a verbal act. The target for this event type is the party that introduces some accusation or charge against the source actor who denies responsibility.                                                                                                                                                                     |
| Example      | The government of Liberia denied on Thursday charges by Ivory Coast that Monrovia is committing genocide.                                                                                                                                                                                                                                      |
| Example      | South Korea on Friday rejected as "totally baseless" accusations by Amnesty International that it had carried out mass arrests of political prisoners, but church human rights groups here supported the accusations.                                                                                                                          |
| NAME         | Engage in symbolic act                                                                                                                                                                                                                                                                                                                         |
| Description  | Engage in symbolic activities such as holding vigils, attending funerals, and laying wreath.                                                                                                                                                                                                                                                   |
| Usage Notes  | Use this event form for all symbolic acts, including those that imply empathy. Use 018 to code only empathetic comments (i.e. not actions).                                                                                                                                                                                                    |
| NAME         | Make empathetic comment                                                                                                                                                                                                                                                                                                                        |
| Description  | Express empathy, condolences, sympathy, understanding.                                                                                                                                                                                                                                                                                         |
| Usage Notes  | This event form refers exclusively to verbal acts or comments. Empathetic and other symbolic actions should be coded as 017 instead.                                                                                                                                                                                                           |
| Example      | Secretary-General Boutros Boutros-Ghali on Saturday expressed condolences to the United States for the death of three American diplomats.                                                                                                                                                                                                      |
| NAME         | Express accord                                                                                                                                                                                                                                                                                                                                 |
| Description  | Express common understanding, agreement, or accord.                                                                                                                                                                                                                                                                                            |
| Usage Notes  | This event form refers exclusively to verbal acts or comments. Use this code when actors indicate that they simply agree or concur on an issue but do not imply commitment or intent to cooperate on that issue. These are typically reciprocal events (see example below) and require coding of more than one 019 event with actors reversed. |
| Example      | President Reagan and Egyptian President Hosni Mubarak agreed today there was an urgent need for progress towards a Middle East settlement and that a freeze on Israeli settlements in occupied territories was also needed.                                                                                                                    |
| Example Note | Two reciprocal events (both 019) are coded with actors reversed.                                                                                                                                                                                                                                                                               |

## 2.2 APPEAL

| NAME        | Make an appeal or request, not specified below                                                                                                                                                                                                                                                                                                                                                                                                      |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | All requests, proposals, suggestions and appeals not otherwise specified. This residual category is not coded except when distinctions among 021                                                                                                                                                                                                                                                                                                    |
| Usage Notes | through 028 cannot be made. Events coded under this category refer to pleas made either on the source actor's own behalf or on behalf of another party (i.e. the source asks that the target does something either for self or for a third party). Note that this and all the subcategories are distinct from demands, which are more forceful, and from pledges, which imply commitments, agreements, or promises on the part of the source actor. |
| NAME        | Appeal for material cooperation                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Description | Make an appeal for, request, or suggest material cooperation.                                                                                                                                                                                                                                                                                                                                                                                       |
| Usage Notes | This event form is typically, though not exclusively, a verbal act. It refers to appeals for material cooperation specifically; appeals for diplomatic cooperation, such as for the provision of support on a particular policy, are coded as 022 instead. (Note that the actual events of material cooperation are coded under category 06.)                                                                                                       |
| Example     | Kenyan President Daniel Arap Moi on Monday urged Uganda to to repatriate "all Kenyan criminals hiding there" to face trial, accusing them of killing Kenyan policemen in cross-border raids recently. Outspoken Serbian ultra-nationalist leader Vojislav Seselj called on Arab countries to join forces against a possible US-led attack on Iraq, Tanjug news agency reported Wednesday.                                                           |
| EXAMPLE     | Kenyan policiemen in cross-border raids recently. Outspoken Serbian ultra-nationalist leader Vojislav Seselj called on Arab countries to join forces against a possible US-led attack on Iraq, Tanjug news agency reported Wednesday.                                                                                                                                                                                                               |
| NAME        | Appeal for economic cooperation                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Description | Make an appeal for, request, or suggest initiating or expanding economic                                                                                                                                                                                                                                                                                                                                                                            |
| Usage Notes | Use this code for requests to develop or expand trade and other forms of economic exchange. Appeals for provision of economic aid-not mutual exchangeare coded as 0231 instead. Actual events of economic cooperation are coded as 061.                                                                                                                                                                                                             |
| Example     | Indian business leaders Friday called for greater impetus towards free trade despite mounting tensions between India and Pakistan.                                                                                                                                                                                                                                                                                                                  |

| NAME        | 0212                                                                                                                                                                                                                                                                                                                                                                                                       |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Make an appeal for, request, or suggest initiating or expanding military ties.                                                                                                                                                                                                                                                                                                                             |
| Usage Notes | Use this code for requests to develop or expand military relations by engaging in acts such as joint military maneuvers or exercises. Appeals for provision of military aid-not mutual exchange-are coded as 0232 instead. Actual events of military cooperation are coded as 062.                                                                                                                         |
| Example     | South Korea has requested to lease a Russian military training ground, mil- itary officers in Seoul said on Thursday.                                                                                                                                                                                                                                                                                      |
| NAME        | Appeal for judicial cooperation                                                                                                                                                                                                                                                                                                                                                                            |
| Description | Make an appeal for, request, or suggest initiating or expanding cooperation in judicial matters.                                                                                                                                                                                                                                                                                                           |
| Usage Notes | Use this code for requests to develop or expand cooperation in such matters as extraditions. Appeals for information or other investigative tools, even if to be used in courts of law, are coded as 0214 instead. Note that in case of extraditions, the target for this event type is not the subject but the country he would be extradited to. Actual events of judicial cooperation are coded as 063. |
| Example     | Turkey renewed an appeal to Belgium to extradite a far-left militant wanted for murder, Justice Minister Cemil Cicek said Thursday, slamming what he called lax international cooperation against terrorism.                                                                                                                                                                                               |
| NAME        | Appeal for intelligence cooperation                                                                                                                                                                                                                                                                                                                                                                        |
| Description | Make an appeal for, request, or suggest sharing of intelligence.                                                                                                                                                                                                                                                                                                                                           |
| Usage Notes | Use this code for requests to develop or expand intelligence and information sharing. Actual events of intelligence cooperation are coded as 064.                                                                                                                                                                                                                                                          |
| Example     | Turkey said Monday it had asked Tehran and Damascus to provide urgent information about arms and ammunition seized last week in southeastern Turkey aboard six trucks travelling from Iran to Syria.                                                                                                                                                                                                       |

| NAME         | 022                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Make an appeal for, request, or suggest expansion of diplomatic ties or co- operation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Usage Notes  | This event form is typically, although not exclusively, a verbal act. It refers to appeals for expanded diplomatic ties and non-tangible support on particular policies. Appeals for more specific forms of diplomacy, such as mediation and negotiation, are coded elsewhere within category 02.                                                                                                                                                                                                                                                                               |
| Example      | North Korean state media have called on the United States to forge "ties of confidence" with Pyongyang ahead of six-party nuclear talks expected to be held in Beijing on July 26.                                                                                                                                                                                                                                                                                                                                                                                              |
| Example      | Charles Taylor called on Liberians to stand by him during these difficult days, "Soon this bad wind shall pass," he moaned.                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Example      | Lebanese President Amin G emayel has asked President Reagan for full United States support for Lebanon's cause, the White House said today.                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| NAME         | Appeal for material aid, not specified below                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Description  | Make an appeal for, request, or suggest provision of material assistance not otherwise specified.                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Usage Notes  | This category contains sub-forms for more detailed coding whenever possible. The source could be requesting aid for itself or on behalf of a third party; in either case, the actor whom the request is directed to should be coded as the target. Note that only requests for or suggestions of material aid are coded under this category; events coded under 023 imply neither the receipt or delivery of material aid nor a commitment on the part of the source actor to provide such aid. For the latter two cases, refer instead to categories 07 and 033, respectively. |
| Example      | Romania has asked the European Community for immediate delivery of ad- ditional aid, EC sources said on Thursday.                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| NAME         | Appeal for economic aid                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Description  | Make an appeal for, request, or suggest economic assistance.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Usage Notes  | This event form is typically, although not exclusively, a verbal act. Requests or suggestions for loans or debt relief are also coded here. Appeals for reciprocal economic exchange, such as trade, should be coded as 0212 instead. The source could be requesting support for itself or on behalf of another party.                                                                                                                                                                                                                                                          |
| Example      | Russia and China will ask Asian banks to help finance construction of an $8 billion Trans-Siberian natural gas link to China.                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Example Note | Because of the compound source (Russia and China), two events are coded.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |

| NAME        | 0232                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Make an appeal for, request, or suggest military assistance.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Usage Notes | This event form is typically, although not exclusively, a verbal act. Requests for or suggestions of joint military actions, rather than unilateral military aid, should be coded as 0212 instead.                                                                                                                                                                                                                                                                                                                                                                                                   |
| Example     | Angola has asked Portugal for military aid, especially instructors for its Soviet- and Cuban-trained armed forces, a Lisbon newspaper said today.                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| NAME        | Appeal for humanitarian aid                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Description | Make an appeal for, request, or suggest humanitarian assistance.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Usage Notes | Requests for or suggestions of food, medicine, and related personnel, as well as shelter and protection, are all coded as 0233. Calls by refugees to be let into the territories of other countries (which should be coded as targets) and asylum requests all fit here. Oxfam Canada today called on the world community to help save tens of thousands of Afghan civilians threatened with starvation.                                                                                                                                                                                             |
| Example     | Oxfam Canada today called on the world community to help save tens of thousands of Afghan civilians threatened with starvation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| NAME        | Appeal for military protection or peacekeeping                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Description | Make an appeal for, request, or suggest deployment of peacekeepers or other military forces to preserve peace, enforce ceasefire, or protect civilians. This event form is typically, although not exclusively, a verbal act. The source actor could be making the appeal for itself or on behalf of another party; the target should represent the actor who is expected to provide the forces.                                                                                                                                                                                                     |
| Example     | A group of prominent Liberals have written to President George Bush urging him to send U.S. peacekeeping troops to their capital Monrovia.                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| NAME        | Appeal for political reform, not specified below                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Description | Make an appeal for, request, or suggest political change not otherwise specified.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Usage Notes | This event form refers to verbal and non-threatening appeals. More force-ful "demands" for political change are coded under 104; expressions that take the form of demonstrations, protests, etc. are coded under category 14. Source actors can be local citizens as well as international actors; they could be making the appeal on their own behalf or on behalf of others. Note that when the requested reform clearly constitutes some form of concession or yielding by the target such as the easing of administrative sanctions, a more appropriate 'Appeal' code might be found under 025. |
| Example     | About 300 representatives from Egyptian civil society organizations submitted the most recent in a series of reform petitions, under the title "In Defense of the Nation" to the Saudi royal family. European ministers had called for Burma to institute reforms before joining the ASEAN.                                                                                                                                                                                                                                                                                                          |

CAMEO

| NAME        | 0241                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Make an appeal for, request, or suggest change in leadership or power.                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Usage Notes | This event form refers to verbal and non-threatening appeals. More forceful "demands" for leadership change are coded as 1041; demonstrations, protests, etc. demanding change in leadership/power are coded under category 14. Note that even though calls for the target to resign or relinquish power are forms of yielding, they are still coded here. Also code appeals for elections here.                                                                                                                     |
| Example     | Members of parliament from Kenya's Liberal Democratic Party called on Energy Minister Kiraitu Murungi to resign in the wake of new evidence over the $7 billion scandals. The UN Security Council has called on Haiti's interim government to hold elections by 7 February.                                                                                                                                                                                                                                          |
| Example     | The UN Security Council has called on Haiti's interim government to hold elections by 7 February.                                                                                                                                                                                                                                                                                                                                                                                                                    |
| NAME        | Appeal for policy change                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Description | Make an appeal for, request, or suggest change in any particular policy.                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Usage Notes | This event form refers to verbal and non-threatening appeals. More forceful "demands" for policy change are coded as 1042; demonstrations, protests, etc. demanding change in leadership/power are coded under category 14. Just like the source actor, the policy in question can also be domestic or international in nature. If it is clear from the lead that by requesting certain policy changes the source is in fact appealing to the target to yield or concede, the event might be better coded under 035. |
| Example     | U.S. President George W. Bush said Friday that he will tell Japanese Prime Minister Junichiro Koizumi that Japan needs to enact significant economic reforms.                                                                                                                                                                                                                                                                                                                                                        |
| Example     | Carl Bildt called for three urgent reforms in Swedish politics-tax reform, business reform and welfare reform-and stressed the creation of new jobs as the principal task for the future.                                                                                                                                                                                                                                                                                                                            |

| NAME        | 0243                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Make an appeal for, request, or suggest provision or expansion of social, political, or other rights.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Usage Notes | This event form refers to verbal and non-threatening appeals. More forceful "demands" for rights are coded as 1043; demonstrations, protests, etc. demanding certain rights are coded under category 14. If it is clear from the lead that by requesting certain rights the source is in fact appealing to the target to yield or concede, the event might be better coded under 025. Appeals for provision of compensation for previously violated rights, for instance, are coded as 025. The UN urged the Maoists rebels in Nepal to honor human rights, according to the UN High Commissioner for Human Rights (UNHCR). The international committee of the Lebanese Living Abroad movement is contacting a number of Lebanese legislatures to propose a new addendum incorporating the right to vote abroad into the electoral law adopted for the upcoming parliamentary elections. |
| EXAMPLE     | The international committee of the Lebanese Living Abroad movement is contacting a number of Lebanese legislatures to propose a new addendum incorporating the right to vote abroad into the electoral law adopted for the upcoming parliamentary elections.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| NAME        | 0244                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Description | Make an appeal for, request, or suggest major institutional, constitutional, or regime change.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Usage Notes | This event form refers to verbal and non-threatening appeals. More forceful "demands" for institutional change are coded as 1044; demonstrations, protests, etc. demanding such change are coded under category 14. Institutional change is different from policy change in that the former directly alters the rules of the game. Requests for fundamental changes in the political system (e.g. democratization) as well as for more limited institutional changes (e.g. changing electoral law) are coded here.                                                                                                                                                                                                                                                                                                                                                                       |
| Example     | President Emile Lahoud has pushed the Lebanese Parliament for a new election law two days before he is to call parliamentary elections.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Example     | Scandal-plagued President Gloria Macapagal Arroyo on Monday urged Congress in the Philippines to change the constitution to shift to a parliamentary form of government to ease the country's constant political instability.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |

| NAME         | Appeal to yield, not specified below                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Make an appeal for, request, or suggest that target yields or concedes; not otherwise specified.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Usage Notes  | This event form is typically, although not exclusively, a verbal act. The source for this event type may or may not be one of the adversaries; a third party could also be appealing to one or more of the parties in conflict (who are coded as targets) to yield. When the source itself expresses its intent to yield-rather than requesting it from another party-the event should be coded under 035 instead. When yielding actually takes place, use the appropriate code under category 08. Israeli Prime Minister Ariel Sharon wants Germany to pay more compensation to the families of 11 Israeli athletes killed at the 1972 Munich Olympic Games, a statement from his office said Tuesday. |
| Example      | CAMEO 0251                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Name         | Appeal for easing of administrative sanction                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Description  | Make an appeal for, request, or suggest that target relaxes administrative restrictions.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Usage Notes  | Use this code when a government is requested to undertake some political changes that clearly constitute some form of concession or yielding, such as relaxing or removing bans or other restrictions that are already in place. Dozens of journalists at Sudan's most respected daily newspaper appealed to the Sudanese government on Wednesday to let them resume publishing and compensate them for lost wages. Human Rights Watch also called on Yemen, Algeria andMalaysia to im-                                                                                                                                                                                                                 |
| Example      | mediately lift bans on newspapers closed in recent days for printing the caricatures. Because of the compound target, three separate events are coded.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Example Note | 0252                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Name         | Appeal for easing of political dissent                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Description  | Make an appeal for, request, or suggest that target stops political protest activities.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Usage Notes  | Use this code for requests for the target to stop engaging in protests, demonstrations, strikes, etc. Islamic fundamentalist leaders appealed to their Muslim followers for an end to anti-government agitation, authorities said Monday.                                                                                                                                                                                                                                                                                                                                                                                                                                                               |

| NAME         | 0253                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Make an appeal for, request, or suggest that target releases persons or property.                                                                                                                                                                                                                                                                                                                                                                                                           |
| Usage Notes  | Use this code for requests for the target to release prisoners, hostages, and any confiscated property.                                                                                                                                                                                                                                                                                                                                                                                     |
| Example      | The United States called on Israel to move forward with its "courageous and historic" disengagement plan as fast as possible.                                                                                                                                                                                                                                                                                                                                                               |
| Example Note | While "disengagement" does not necessarily involve any kind of release of persons or property, in the case of Israel we can safely assume that any mention of the "disengagement plan" refers primarily to the withdrawal of settlements, hence, the return of land to the Palestinians; phrases involving "disengagement" or "settlements" can be entered into verb dictionaries, particularly the Middle East dictionary, as the appropriate codes pertaining to the release of property. |
| NAME         | Appeal for easing of economic sanctions, boycott, or embargo                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Description  | Make an appeal for, request, or suggest that target stops or eases economic sanctions, boycott, or embargo.                                                                                                                                                                                                                                                                                                                                                                                 |
| Usage Notes  | Use this code only for economic sanctions, boycotts, or embargoes.                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Example      | Iraq on Saturday appealed to the U.N. to bring an end to their trade embargo, which it said is causing huge shortages of medicine and food.                                                                                                                                                                                                                                                                                                                                                 |
| NAME         | Appeal to allow international involvement (non-mediation)                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Description  | Make an appeal for, request, or suggest that target allows the entry of international actors, such as observers, humanitarian agencies, and peacekeeping forces.                                                                                                                                                                                                                                                                                                                            |
| Usage Notes  | Requests for adversaries to allow mediation are coded as 028 instead.                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Example      | An international aid agency appealed to the Sudanese government on Friday to urgently reconsider its ban on relief flights to southern Sudan.                                                                                                                                                                                                                                                                                                                                               |
| Example Note | Because the identity of the agency is not provided, the general NGO code will be used.                                                                                                                                                                                                                                                                                                                                                                                                      |

| NAME        | 0256                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Make an appeal for, request, or suggest that target stops fig ting or takes measures to ease military conflict or tension.                                                                                                                                                                                                                                                                                                                                                                                                          |
| Usage Notes | Use this code for appeals for ceasefires, military withdrawals, and demobilization.                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Example     | The presidents of Iraq and Egypt called on Tuesday for the withdrawa l of Syrian and other foreign forces from Lebanon to end 14 years of civil war there. Because of the compound source (governments of Iraq and Egypt), two events are coded. Leaders of the 16-member Economic Community of West African States (ECOWAS) called on Wednesday for an immediate ceasefire in war-torn Liberia.                                                                                                                                    |
| EXAMPLE     | CAMEO 026                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Name        | Appeal to others to meet or negotiate                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Description | Propose or suggest meeting, negotiation, or discussion among other parties. This event form is typically, although not exclusively, a verbal act. The source for this event cannot be the actors whose meeting or negotiation is called for ; it has to be third parties who appeal to one or more actors- target actors-to meet and/or negotiate. When parties themselves express their intent to meet and/or negotiate, use 036 instead. When meetings or negotiations do take place, use the appropriate code under category 04. |
| Example     | El Salvador on Monday requested an urgent Security Council meeting on Wednesday to deal with what it called violations by Nicaragua of the Central American peace accords.                                                                                                                                                                                                                                                                                                                                                          |
| NAME        | Appeal to others to settle dispute                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Description | Propose or suggest that others reach a settlement, agreement, or resolution of conflict.                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Usage Notes | This event form is typically, although not exclusively, a verbal act. Note that the source for this event cannot be the adversaries themselves . When one or more parties to a conflict call for ending the conflict, that is taken to be an expression of intent on the part of that source actor to reach a settlement and is thus coded as 037 instead. The Russian Foreign Minister Sergei Lavrov said here Saturday that he urges                                                                                              |
| Example     | Iran and the EU trio (France, Germany, and Britain) to reach an agreement in their talks on Iran's nuclear program. Given the presence of four different targets, four events are coded.                                                                                                                                                                                                                                                                                                                                            |

| NAME        | CAMEO                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 028   |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|
| Description | Propose or suggest that target mediates or accepts the mediation of others. This event form is typically, although not exclusively, a verbal act. Note that the source for this event cannot be the potential mediator or parties to the conflict. When an actor proposes to play the role of mediator himself, this is assumed to be a commitment on his part and is coded as 039 instead. When one or more of the adversaries request that another party plays the role of a mediator, this is understood to be a commitment on their part to accept mediation and is thus coded as 038. The target can either be a potential mediator (whose mediation is being requested) or one of the adversaries (who is requested to allow involvement of mediators). The International Crisis Group has called on the UN stabilization mission in Haiti to broker an agreement among Haitians that "establishes common objectives for the next government." |       |
| Example     | in Haiti to broker an agreement among Haitians that "establishes common objectives for the next government."                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |       |

## 2.3 EXPRESSENT TO COOPERATE

| NAME        | CAMEO                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 030                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Express intent to cooperate, not specified below Offer, promise, agree to, or otherwise indicate willingness or commitment to cooperate not otherwise specified. This residual category is not coded except when distinctions among codes 031 through 039 cannot be made. All cooperative actions reported in future tense are also taken to imply intentions, if not promises or commitments, to cooperate and are hence coded under this category. These events can be reciprocal or unilateral. | Express intent to cooperate, not specified below Offer, promise, agree to, or otherwise indicate willingness or commitment to cooperate not otherwise specified. This residual category is not coded except when distinctions among codes 031 through 039 cannot be made. All cooperative actions reported in future tense are also taken to imply intentions, if not promises or commitments, to cooperate and are hence coded under this category. These events can be reciprocal or unilateral. Senior Hungarian and Romanian officials agreed on Wednesday that their countries should cooperate to encourage Romanian refugees in Hungary to return home. Two reciprocal events are coded with actors reversed. |

| Name             | 031                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Express intent to engage in material cooperation, not specified below                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description      | Offer, promise, agree to, or otherwise indicate willingness or commitment to engage in or expand material cooperative exchange not otherwise specified. This category contains sub-forms for more detailed coding whenever possible. This event form refers to commitments or indications of intent by parties to boost their material exchange ; they could be reciprocal or unilateral agreements, promises, commitments, or other indications of intent to cooperate. Pledges to provide unilateral material aid, however, are coded under category 033. Expressions of intent to engage in or further diplomatic cooperation, such as negotiations, settling disputes, or provision of policy support are coded elsewhere under category 03. Note that events coded here are intents and commitments, and not actual events of cooperation, which should be coded under 06. The Asia-Pacific Economic Cooperation (APEC) forum has agreed to set up an energy research center in Tokyo to further develop its regional energy projections, officials said Thursday. | Offer, promise, agree to, or otherwise indicate willingness or commitment to engage in or expand material cooperative exchange not otherwise specified. This category contains sub-forms for more detailed coding whenever possible. This event form refers to commitments or indications of intent by parties to boost their material exchange ; they could be reciprocal or unilateral agreements, promises, commitments, or other indications of intent to cooperate. Pledges to provide unilateral material aid, however, are coded under category 033. Expressions of intent to engage in or further diplomatic cooperation, such as negotiations, settling disputes, or provision of policy support are coded elsewhere under category 03. Note that events coded here are intents and commitments, and not actual events of cooperation, which should be coded under 06. The Asia-Pacific Economic Cooperation (APEC) forum has agreed to set up an energy research center in Tokyo to further develop its regional energy projections, officials said Thursday. |
| Example          | The Asia-Pacific Economic Cooperation (APEC) forum has agreed to set up an energy research center in Tokyo to further develop its regional energy projections, officials said Thursday.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | The Asia-Pacific Economic Cooperation (APEC) forum has agreed to set up an energy research center in Tokyo to further develop its regional energy projections, officials said Thursday.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| NAME Description | Express intent to cooperate economically Offer, promise, agree to, or otherwise indicate willingness or commitment to engage in or expand economic ties. This event form refers to agreements, promises, commitments, or other indications of intent to develop or expand trade and other forms of economic exchange. Offers, promises, or commitments by one actor to provide eco-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | This event form refers to agreements, promises, commitments, or other indications of intent to develop or expand trade and other forms of economic exchange. Offers, promises, or commitments by one actor to provide eco-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Example          | The United States and Jordan have agreed upon a new free-trade pact between the two countries, the White House announced Tuesday. Two reciprocal events are coded with actors reversed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | The United States and Jordan have agreed upon a new free-trade pact between the two countries, the White House announced Tuesday. Two reciprocal events are coded with actors reversed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| NAME Description | Express intent to cooperate militarily Offer, promise, agree to, or otherwise indicate willingness or commitment to engage in or expand military ties. This event form refers to agreements, promises, commitments, or other indications of intent to develop or expand military relations by engaging in such acts as joint military maneuvers or exercises. Offers, promises, or commitments by one actor to provide military aid to another should be coded as                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Express intent to cooperate militarily Offer, promise, agree to, or otherwise indicate willingness or commitment to engage in or expand military ties. This event form refers to agreements, promises, commitments, or other indications of intent to develop or expand military relations by engaging in such acts as joint military maneuvers or exercises. Offers, promises, or commitments by one actor to provide military aid to another should be coded as                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Example          | Jordan and Britain have agreed to undertake joint military exercises this month, a Jordanian official confirmed. Two reciprocal events are coded with actors reversed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Jordan and Britain have agreed to undertake joint military exercises this month, a Jordanian official confirmed. Two reciprocal events are coded with actors reversed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |

| NAME        | 0313                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Offer, promise, agree to, or otherwise indicate willingness or commitment to engage in or expand judicial cooperation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Usage Notes | This event form refers to agreements, promises, commitments, or other indications of intent to develop or expand judicial cooperation by engaging in such acts as extraditions.                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Example     | Libya has offered to hand over to an Arab country two of its nationals suspected by the West of blowing up a Pan Am plane in 1988, a state-owned Egyptian newspaper said.                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| NAME        | Express intent to cooperate on intelligence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Usage Notes | Offer, promise, agree to, or otherwise indicate willingness or commitment to engage in or expand intelligence sharing. This event form refers to agreements, promises, commitments, or other indications of intent to develop or expand intelligence cooperation by providing or exchanging intelligence or information. Israel and the Palestinians reached a consensus to exchange information on water resources on the second day of a multilateral conference on water problems in the Middle East here Thursday, the meeting's co-chairman said. Two reciprocal events are coded with actors reversed. |
| Example     | The Turkish-Cypriot and Greek-Cypriot sides of this divided Mediterranean island have agreed to share information Friday on missing people from both communities, a UN official said on Monday. Two reciprocal events are coded with actors reversed.                                                                                                                                                                                                                                                                                                                                                        |
| NAME        | Express intent to engage in diplomatic cooperation (such as policy support)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Description | Expand diplomatic ties or cooperation. This event form is typically, although not exclusively, a verbal act. The offered or promised support should be non-material, such as supporting or backing particular policies and/or goals. Note that agreements or promises to engage in more specific forms of diplomatic cooperation, such as negotiations and mediation, are coded elsewhere under category 03. The target should be the recipient of the potential support.                                                                                                                                    |
| Example     | Portugal will support Turkey's efforts to become a full member of the European Community, Portuguese President Mario Soares said on Tuesday. Note that the future tense used in the lead indicates future commitment. Hungary has said it will support a U.N. Security Council resolution that aims to tighten sanctions and impose a naval blockade against neighboring Yugoslavia. Note that the future tense used in the lead indicates future commitment.                                                                                                                                                |

| NAME         | Express intent to provide material aid, not specified below                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Offer, promise, agree to, or otherwise indicate willingness or commitment to provide some form of material support not otherwise specified. This event category contains sub-forms for more detailed coding whenever possible. Note that more general commitments to broaden material exchange or cooperation are coded under 031 instead. Reported deliveries of material support are coded under category 07. The target should be the prospective recipient of aid. NATO-member Norway is willing to send material to help defend Saudi Arabia if it is attacked, Norway's foreign minister said. |
| Example      | Arabia if it is attacked, Norway's foreign minister said.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| NAME         | Express intent to provide economic aid                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Description  | Offer, promise, agree to, or otherwise indicate willingness or commitment to provide economic support.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Usage Notes  | Code commitments to provide financial support, in form of grants, loans, or debt relief under this event code. Trade commitments should be coded as 0311 instead.                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Example      | Finland will give Tanzania a grant of 580 million shillings (64.45 million dollars) over the next three years to finance several projects in the country, a statement issued by the ministry of finance said today.                                                                                                                                                                                                                                                                                                                                                                                  |
| Example      | Note that the future tense used in the lead indicates future commitment. European Community foreign ministers agreed in principle on Saturday to provide about 70 million dollars of aid for Romania and Poland. Due to the compound target actor, two events are coded.                                                                                                                                                                                                                                                                                                                             |
| Example Note | Express intent to provide military aid                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| CAMEO        | 0332                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Name         | Offer, promise, agree to, or otherwise indicate willingness or commitment to provide military support.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Usage Notes  | Use this event form to code commitments to provide all forms of military aid. Promises to engage in bilateral or multilateral military cooperation should be coded as 0312 instead.                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Example      | British Defence Secretary Tom King has promised to continue military aid to war-torn Mozambique.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Example      | Syria has again offered its troops to Lebanon's new President Elias Hrawi to help him oust General Michel Aoun from the Christian enclave Aoun controls.                                                                                                                                                                                                                                                                                                                                                                                                                                             |

| NAME        | 0333                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Offer, promise, agree to, or otherwise indicate willingness or commitment to provide humanitarian support.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Usage Notes | Use this code for commitments to provide all forms of humanitarian aid, including evacuations from dangerous zones and shelter for refugees. However, note that expressions of intent to provide military security or peacekeeping forces are coded as 0334 instead. Actual provisions of humanitarian aid are coded as 073.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Example     | The United Nations will provide nearly 25,000 tons of emergency food aid to refugees fleeing the civil war in Liberia, the World Food Program (WFP) said on Monday.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| NAME        | Express intent to provide military protection or peacekeeping                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Usage Notes | Offer, promise, agree to, or otherwise indicate willingness or commitment to deploy peacekeeping or other military forces for security. Source actor for this event is the party making the commitment to provide forces, while the target represents the prospective location of deployment. Actual deployments should be coded as linked events 'Provide military protection or peacekeeping' (074) and 'Receive deployment of peacekeepers' (0861) with actors reversed. Commitments by adversaries to accept peacekeepers should be coded as 0355. France is ready to contribute up to 4,000 troops to an international peace- keeping force in Yugoslavia, Defence Minister Pierre Joxe said on Monday. The Security Council today agreed to a six-month extension of the mandate for the peacekeeping force in Lebanon (UNIFIL) despite Israel's wish for a shorter period. |
| Example     | The Security Council today agreed to a six-month extension of the mandate for the peacekeeping force in Lebanon (UNIFIL) despite Israel's wish for a shorter period.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| NAME        | Express intent to institute political reform, not specified below                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Description | Offer, promise, agree to, or otherwise indicate willingness or commitment to institute political change not otherwise specified. If the promised reforms clearly constitutes some form of concession or yielding by the source, such as the easing of existing administrative sanctions, a more appropriate code might be found under 035. If there are specific groups or individuals asking for that change and that information is codeable given the structure of the lead, those actors should be coded as targets; otherwise, the country in general or actors to be affected by the change should be coded as the target.                                                                                                                                                                                                                                                  |

CAMEO

| NAME         | 0341                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Offer, promise, agree to, or otherwise indicate willingness or commitment to                                                                                                                                                                                                                                                                                                                                                                                                   |
| Usage Notes  | Commitments to resign or hand over power, as well to hold elections that might open the way for change in leadership, are coded here. Note that while commitments for other forms of yielding are coded under 035, commitments to give up power are coded here. Ousted President Askar Akyev has agreed to resign without returning to the Kyrgyzstan, the Parliament speaker said Saturday. Because no specific group is mentioned, the country alone is coded as the target. |
| Example      | CAMEO 0342                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Name         | Express intent to change policy                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Usage Notes  | Use this code for commitments to bring policy change-political, economic, military, social, or otherwise. If the policy change in question clearly represents a form of yielding, the appropriate code under 035 should be used instead.                                                                                                                                                                                                                                       |
| Example      | Planning and Investment Minister Tran Xuan Gia said Vietnam is committed to opening up the economy but will not be rushed, in a rare interview late on Friday. Vietnam can be coded as the target since the country in general is obviously going to be affected from such a change in policy.                                                                                                                                                                                 |
| CAMEO        | 0343                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Name         | Express intent to provide rights                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Description  | Offer, promise, agree to, or otherwise indicate willingness or commitment to provide social, political, economic, or other rights and freedoms. If it is clear from the lead that by promising to provide certain rights the source is in fact committing to yield, the event might be better coded under 035. Commitments to provide compensation for previously violated rights, for instance, are coded as 035.                                                             |
| Example      | Turkey will allow up to 13,000 Turkish Kurd refugees who have lived in Iraq for more than a decade to return home as part of a UN-brokered deal.                                                                                                                                                                                                                                                                                                                               |
| Example Note | Allowing the voluntary repatriation of refugees constitutes provision of the right to go home.                                                                                                                                                                                                                                                                                                                                                                                 |

| NAME                | 0344                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description         | Express intent to change institutions, regime Offer, promise, agree to, or otherwise indicate willingness or commitment to make fundamental political changes, such as moving from one type of political system to another and reforming political institutions or key laws. Note the difference between institutional/regime changes and policy reforms. Serbian President Vojislav Kostunica promised to democratize Serbia and establish the rule of law as he succeeded Milosevic. |
| Usage Notes Example | Serbian President Vojislav Kostunica promised to democratize Serbia and establish the rule of law as he succeeded Milosevic.                                                                                                                                                                                                                                                                                                                                                           |
| NAME                | Express intent to yield, not specified below                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Description         | Offer, promise, agree to, or otherwise indicate willingness or commitment to yield not otherwise specified.                                                                                                                                                                                                                                                                                                                                                                            |
| Usage Notes         | This event form refers to general expressions of willingness or commitment to concede; use the subcategories for more detailed coding. The actual events of yielding are coded under category 08.                                                                                                                                                                                                                                                                                      |
| Example             | A Soviet official offered concessions last November that U.S. negotiator Paul Nitze believed could lead to an agreement on reducing nuclear missiles in Europe, according to a senator who acted as a go-between at the talks.                                                                                                                                                                                                                                                         |
| NAME                | Express intent to ease administrative sanctions                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Description         | Offer, promise, agree to, or otherwise indicate willingness or commitment to ease administrative sanctions, such as censorship, curfew, state of emergency, and martial law.                                                                                                                                                                                                                                                                                                           |
| Example             | In an interview this weekend, President Abdelaziz Bouteflika said he is prepared to lift ban on Islamic Salvation Front (FIS) but not with its historical leadership.                                                                                                                                                                                                                                                                                                                  |
| NAME                | Express intent to ease popular dissent                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Description         | Offer, promise, agree to, or otherwise indicate willingness or commitment to reduce or stop political protest activities, such as demonstrations and rallies. Leaders of the Azadliq (Freedom) opposition coalition agreed to postpone the demonstration in Baku until 9 November.                                                                                                                                                                                                     |

| NAME         | 0353                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Offer, promise, agree to, or otherwise indicate willingness or commitment to release or return persons or property.                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Usage Notes  | Commitments to release or exchange prisoners and hostages, as well as committments to return previously confiscated properties, are coded here.                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Example      | The Fijian rebels said they will release Prime Minister Mahendra Chaudhry and more than 30 members of his government, whom they had taken hostage two weeks ago, on the weekend. The rebel Revolutionary United Front (RUF) announced it will return weapons and military equipment seized last year from United Nations peace- keepers, according to reports reaching here from the country's capital Free- town. Under the disengagement plan, Isreal will evacuate all 21 settlements in the Gaza Strip in mid-August, said spokesperson for the Israeli prime minister. |
| Example      | Under the disengagement plan, Isreal will evacuate all 21 settlements in the Gaza Strip in mid-August, said spokesperson for the Israeli prime minister.                                                                                                                                                                                                                                                                                                                                                                                                                    |
| NAME         | Express intent to ease economic sanctions, boycott, or embargo                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Description  | Offer, promise, agree to, or otherwise indicate willingness or commitment to reduce or eliminate economic sanctions, boycotts, or embargoes.                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Usage Notes  | Use this code only for economic sanctions, boycotts, or embargoes.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Example      | The US Congress agreed to lift embargoes on pharmaceutical sales in late February to Iran, Libya, North Korea, Sudan, and with strings attached, Cuba.                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Example Note | Due to the compound target, five separate events are coded.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| NAME         | Express intent to allow international involvement (non-mediation)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Description  | Offer, promise, agree to, or otherwise indicate willingness or commitment to allow access to international actors, such as observers, humanitarian agencies, and peacekeeping forces.                                                                                                                                                                                                                                                                                                                                                                                       |
| Usage Notes  | Prospective peacekeepers, observers, etc. are coded as targets. Commitments to accept mediation by third parties are coded as 038 instead.                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Example      | Ethopia has agreed to re-open its borders to UN peacekeepers, who are de- polyed in the region to oversee a ceasefire between Ethiopia and its neighbor, Eritrea.                                                                                                                                                                                                                                                                                                                                                                                                           |
| Example      | In a letter handed over to the United Nations on Monday, Iraq said it would allow the return of U.N. weapons inspectors "without conditions" to "remove any doubts Iraq still possesses weapons of mass destruction."                                                                                                                                                                                                                                                                                                                                                       |
| Example      | With the signing of a Memorandum of Understanding (MOU) on Cessation of Hostilities, the Sudanese government and SPLM/A have agreed to allow "unimpeded humanitarian access to all areas and for people in need."                                                                                                                                                                                                                                                                                                                                                           |
| Example Note | Two reciprocal events are coded with actors reversed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |

CAMEO

| NAME        | 0356                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Offer, promise, agree to, or otherwise indicate willingness or commitment to stop fighting or take measures to ease military conflict or tension.                                                                                                                                                                                                                                                                                       |
| Usage Notes | Use this code for appeals for ceasefire, military withdrawals, and demobilization.                                                                                                                                                                                                                                                                                                                                                      |
| Example     | Yugoslavia and Slovenia agreed to a ceasefire after two days of fierce fighting but media reports said sporadic clashes were still continuing.                                                                                                                                                                                                                                                                                          |
| Example     | Two reciprocal events are coded with actors reversed. Shefket Musliu said on 21 May in Konculj, in the Federal Republic of Yugoslavia, that his forces will lay down their weapons and disband by the end of the month because "the time has come. . . . to seek changes through political means," AP reported.                                                                                                                         |
| Example     | Syria says it is willing to withdraw its troops from neighboring Lebanon, after fifteen years of effective military occupation.                                                                                                                                                                                                                                                                                                         |
| NAME        | Express intent to meet or negotiate                                                                                                                                                                                                                                                                                                                                                                                                     |
| Description | Offer, promise, agree to, or otherwise indicate willingness or commitment to meet, visit, or engage in talks or negotiations. This event code refers to future commitments to meet and/or negotiate; when meetings, negotiations, or other talks do take place, those are coded under category 04 instead. When mediation is mentioned specifically, appropriate mediation-related codes take precedence over meetings or negotiations. |
| Usage Notes | appropriate mediation-related codes take precedence over meetings or negotiations. East German Foreign Minister Oskar Fischer will visit Albania in June, the first Warsaw Pact foreign minister to do so since Tirana split with Moscow in 1961, the Albanian embassy said. Given the wording of this lead, which implies that Albania has already com-                                                                                |
| Example     | mitted to receive the German minister, two reciprocal events of 038 are coded with actors reversed. This example fits under this category since the future tense used implies a future commitment to meet.                                                                                                                                                                                                                              |
| Example     | On September 29, Putin offered to negotiate with Chechen President Aslan Maskhadov following the invasions of Dagestan. Unlike the previous example, this lead does not suggest that Maskhadov has also committed to meeting with Putin, hence only one 036 event is coded with the Russian government as the source actor.                                                                                                             |

CAMEO

| NAME        | Express intent to settle dispute                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Offer, promise, agree to, or otherwise indicate willingness or commitment to reach a comprehensive settlement, agreement, or resolution to conflict.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Usage Notes | Note that specific commitments to yield, which might be present steps to settling disputes, are coded elsewhere under category 03. Both the source and the target for this event type should be adversaries themselves. When other parties make appeals to end disputes in which they are not directly involved, use 'Appeal to others to settle dispute' (027) instead.                                                                                                                                                                                                                                                                                                                                |
| Example     | Denmark today accepted a formula for ending its fisheries dispute with its European common market partners, government officials said.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| NAME        | Express intent to accept mediation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Description | Offer, promise, agree to, or otherwise indicate willingness or commitment to accept mediation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Usage Notes | This code represents adversaries' commitments to receive mediation by third parties. The latter should be coded as targets, while the source has to be one or more of the parties in conflict for this event. Note that when reports involve references to mediation specifically, mediation-related codes such as this take precedence over others, such as 'Agree to meet or negotiate,' 'Make a visit,' 'Host a visit,' and 'Meet at a third location.' For commitments by third parties to mediate refer to code 039 instead. For simple suggestions by actors other than adversaries and potential mediators that mediation occurs, use 'Appeal to others to engage in or accept mediation' (028). |
| Example     | Afghan rebel leaders said on Wednesday they would meet U.N. mediator Diego Cordovez if he gave them a veto over any settlement reached in peace talks. Israeli Prime Minister Ehud Barak has agreed to US mediation in the final status talks with the Palestinians, a senior Israeli official said.                                                                                                                                                                                                                                                                                                                                                                                                    |

| NAME         | Express intent to mediate                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Offer, promise, agree to, or otherwise indicate willingness or commitment to play the role of a mediator. This code represents a commitment by third parties to mediate between parties in conflict. The former should be coded as source and the later as targets for this event. Note that when reports involve references to mediation speci- cally, mediation-related codes such as this take precedence over others , such as 'Agree to meet or negotiate,' 'Make a visit,' 'Host a visit,' and 'Meet at a third location.' For commitments of adversaries to accept mediation by actors other than the adversaries and potential mediators that mediation occurs, refer to 'Appeal to others to engage in or accept mediation' (028). |
| Example      | Gambian President Dawda Jawara will visit Mauritania and Senegal to medi- ate in a border dispute between the two West African neighbors, diplomatic sources said on Wednesday.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Example Note | Given the wording used in this particular lead, which implies that Mauritania and Senegal have already agreed to Gambia's mediation, two types of linked events are coded- 'Express intent to mediate' (039) with the Gambian president as the source, and 'Express intent to accept mediation' (038) with Mauritania and Senegal as sources. Two different events are coded for each of these event types since Mauritania and Senegal are compound actors. King Hassan of Morocco was quoted today as saying he would be ready to host a meeting between an Israeli peace movement and the Palestine Liberation Organization (PLO).                                                                                                       |
| Example Note | Unlike the previous example, this lead does not imply that either the Israeli or the Palestinian parties have accepted King Hassan's offer to mediate, hence no 'Agree to mediation' event is coded. Given the compound target, two separate 039 events are coded.                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

## 2.4 CONSULT

| CAMEO       | 040                                                                                                                                                                                                                                                                                                                                                                     |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | Consult, not specified below                                                                                                                                                                                                                                                                                                                                            |
| Description | All consultations and meetings not otherwise specified.                                                                                                                                                                                                                                                                                                                 |
| Usage Notes | This residual category is not coded except when distinctions among 041 through 046 cannot be made. Note that events coded under 04 are typically, although not always, reciprocal events.                                                                                                                                                                               |
| Example     | A group of African diplomats held their first meeting with President Par- vanov at a lunch hosted by the Ambassador of Kingdom of Morocco. This lead is coded as 040 since the place of the meeting is not explicit in the lead, hence we cannot code it as a visit made or hosted, and no negotiations are implied (so, we cannot code it as 'Engage in negotiation'). |

| NAME         | Discuss by telephone                                                                                                                                                                                                                                                                               |
|--------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Consult, talk on the telephone.                                                                                                                                                                                                                                                                    |
| Usage Notes  | This is typically a reciprocal event. The nature of the phone conversation is not of significance.                                                                                                                                                                                                 |
| Example      | U.S. Secretary of State Warren Christopher telephoned Russian Foreign Minister Andrei Kozyrev on Tuesday to discuss efforts to forge a peace settlement in former Yugoslavia, Itar-Tass news agency said. Two events of the same type are coded with actors reversed.                              |
| Example Note | Two events of the same type are coded with actors reversed.                                                                                                                                                                                                                                        |
| NAME         | Make a visit                                                                                                                                                                                                                                                                                       |
| Description  | Travel to another location for a meeting or other event.                                                                                                                                                                                                                                           |
| Usage Notes  | All visits and travels should be coded under this category. Note that this event is typically accompanied by the linked event 'Host a visit' (043). If mediation or negotiation is mentioned specifically as having taken place, those events take precedence over unspecified visits or meetings. |
| Example      | Taiwan's Vice Foreign Minister visited Russia today, becoming the island's highest ranking government official to go there.                                                                                                                                                                        |
| Example Note | Two events are coded: 042 with the Taiwanese government as the source and Russia as the target, and 043 with actors reversed.                                                                                                                                                                      |
| Example Note | Iraqi President Saddam Hussein arrived in Amman on a previously unannounced visit on Wednesday. Two events are coded: 042 with the Iraqi government as the source and Jordan as the target, and 043 with actors reversed.                                                                          |
| NAME         | Host a visit                                                                                                                                                                                                                                                                                       |
| Description  | Host or receive a visitor at residence, office or home country.                                                                                                                                                                                                                                    |
| Usage Notes  | This event is typically accompanied by the linked event 'Make a visit' (042). If mediation or negotiation is mentioned specifically as having taken place, those events take precedence over unspecified visits or meetings.                                                                       |
| Example      | Russian President Boris Yeltsin on Saturday hosted Japanese Prime Minister Ryutaro Hashimoto in this Siberian city for an informal meeting aimed at establishing close personal relations between the two leaders.                                                                                 |
| Example Note | Two events are coded: 043 with the Russian government as the source and the Japanese government as the target, and 042 with the actors reversed.                                                                                                                                                   |
| Example      | President Francois Mitterand gave a warm welcome on Thursday to South African leader F.W. de Klerk who is attempting to break his country's international isolation.                                                                                                                               |
| Example Note | Two events are coded: 043 with the French government as the source and the South African government as the target, and 042 with actors reversed.                                                                                                                                                   |

| CAMEO        | 044                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name         | Meet at a 'third' location                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Description  | Meet, come together, gather with others at a neutral location-some place with which none of the attending parties are associated. If mediation or negotiation is mentioned specifically as having taken place, those events take precedence over unspecified visits or meetings. This event type is typically accompanied by two other linked events, 'Make a visit' (042) and 'Host a visit' (043), and the event itself is reciprocal. For 044, the source and the target are the actors who are meeting; the location of the meeting is ignored.   |
| Example      | U.S. and Soviet negotiators return to Geneva this week for talk on limiting the number of European-based nuclear missiles, an issue likely to dominate East-West relations this year.                                                                                                                                                                                                                                                                                                                                                                 |
| Example Note | Six events are coded: two reciprocal 'Meet at a third location' events with US and the Soviet Union as actors; two ''Make a visit' events with Switzerland as the target, and the US and the Soviet Union as the two different sources; and two 'Host a visit' events with Switzerland as the source and the US and the Soviet as the two different targets.                                                                                                                                                                                          |
| CAMEO        | 045                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Name         | Engage in mediation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Description  | Mediate between two or more parties.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Usage Notes  | This event code should be used only when a party meets with others explicitly as a mediator. The source is always the mediator and adversaries are the targets. All other cases of meetings and negotiations, where the pur- pose of the meeting or the role of the source actor is not specified, should be coded elsewhere under category 04. If meetings, discussions, or negoti- tions are explicitly reported as involving mediators, the mediation code takes precedence as long as the party acting as the mediator is identified in the lead. |
| Example      | Arab League Secretary General Chadli Klibi undertook mediation mission between Syria and Palestinian leader Yasser Arafat.                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Example Note | Because of the compound target actor, two events are coded. Quatar's emir, Sheikh Hamad bin Khalifa al-Thani launched a mediation                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Example Note | been strained by Riyadh's new friendship with Tehran. Because of the compound target actor, two events are coded.                                                                                                                                                                                                                                                                                                                                                                                                                                     |

| NAME         | Engage in negotiation                                                                                                                                                                                                                                                                                                               |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Negotiate or bargain with others.                                                                                                                                                                                                                                                                                                   |
| Usage Notes  | This event code should be used only when the report makes clear that negotiations, bargaining, or discussions are involved in the meetings or consultations in question. "Holding talks" and "discussions" are treated as negotiations. These are reciprocal events.                                                                |
| Example      | Israel and Lebanon renewed negotiations today on an Israeli troop pullback from Lebanon and their future relations.                                                                                                                                                                                                                 |
| Example Note | Two 046 events are coded with actors reversed. French National Assembly president Laurent Fabius and a group of deputies held talks with leaders of Romania's new government on Tuesday, the first high level Western delegation to visit Bucharest since last month's revolu- tion. Two 046 events are coded with actors reversed. |

## 2.5 ENGAGE IN DIPLOMATIC COOPERATION

| CAMEO       | 050                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | Engage in diplomatic cooperation, not specified below                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Description | Initiate, resume, improve, or expand diplomatic, non-material cooperation or exchange not otherwise specified. This residual category is not coded except when the support in question cannot be further specified and codes 051-057 cannot be used. Czechoslovakia and Albania have upgraded their diplomatic ties back up to ambassadorial level after an 18-year break, the official CTK news agency said on Wednesday. Two reciprocal events are coded with actors reversed. |
| Example     | Two reciprocal events are coded with actors reversed.                                                                                                                                                                                                                                                                                                                                                                                                                            |
| CAMEO       | 051                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Name        | Praise or endorse                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Description | Express support for, commend, approve policy, action, or actor.                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Usage Notes | This event form is typically, although not exclusively, a verbal act. A top U.S. official today praised Haiti's efforts to improve its record on human rights and said it was an important partner for the United States. The West German government today welcomed President Reagan's latest policy statement as proof of Washington's earnest wish for a settlement to be reached in U.S.-Soviet nuclear talks.                                                                |

| CAMEO       | 051                                                                                                                                                                                                                                                                                                                                                                                                               |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | Praise or endorse                                                                                                                                                                                                                                                                                                                                                                                                 |
| Description | Express support for, commend, approve policy, action, or actor.                                                                                                                                                                                                                                                                                                                                                   |
| Usage Notes | This event form is typically, although not exclusively, a verbal act. A top U.S. official today praised Haiti's efforts to improve its record on human rights and said it was an important partner for the United States. The West German government today welcomed President Reagan's latest policy statement as proof of Washington's earnest wish for a settlement to be reached in U.S.-Soviet nuclear talks. |

| NAME         | Defend verbally                                                                                                                                                                                                                                                                    |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Defend verbally, justify policy, action or actor.                                                                                                                                                                                                                                  |
| Usage Notes  | This event form is a verbal act. Use this code only for political, diplomatic, and non-material defense; military cooperation or defense should be coded elsewhere.                                                                                                                |
| Example      | The United States on Thursday defended the right of Soviet troops to fire protectively on militants in Azerbaijan and insisted unrest there reflected age-old ethnic tensions, not a fight for political independence.                                                             |
| Example      | Palestinian leader Yasser Arafat defended Iraq and Libya on Friday against Western criticism of their arms industries and said the West was applying double standards on human rights. Because of the compound target, two events are coded.                                       |
| Example Note | 053                                                                                                                                                                                                                                                                                |
| Name         | Rally support on behalf of                                                                                                                                                                                                                                                         |
| Description  | Call on other parties to support the target.                                                                                                                                                                                                                                       |
| Usage Notes  | This event form is typically, although not exclusively, a verbal act. Use this event form to code instances where one party (the source) solicits the support of third parties for another party (the target).                                                                     |
| Example      | Arab League Secretary-General Chedli Klibi today urged the European Community to support the Palestinian Liberation Organization (PLO), which he said would create a favorable climate for peace talks.                                                                            |
| Example      | Saudi Arabia has mobilized pressure groups in the United States to help support the rights of Palestinians in their struggle against Israel, a top minister said in comments published Thursday.                                                                                   |
| CAMEO        | 054                                                                                                                                                                                                                                                                                |
| Name         | Grant diplomatic recognition                                                                                                                                                                                                                                                       |
| Description  | Grant diplomatic recognition, initiate diplomatic relations with a state or a                                                                                                                                                                                                      |
| Usage Notes  | This event form is typically, although not exclusively, a verbal act. Recognition of newly independent states, new governments that might have come to power through unconventional means, and initiation of diplomatic ties with an entity for the first time are all coded here. |
| Example      | Sri Lanka has established diplomatic ties with and opened an embassy in Tehran, the foreign ministry said on Wednesday.                                                                                                                                                            |
| CAMEO        | 055                                                                                                                                                                                                                                                                                |
| Name         | Apologize                                                                                                                                                                                                                                                                          |
| Description  | Express regret or remorse for an action or situation.                                                                                                                                                                                                                              |
| Usage Notes  | Although this event form is typically a verbal act, it should also be used to code all nonverbal acts that express remorse.                                                                                                                                                        |
| Example      | Argentina has apologized to Brazil for one of its gunboats intercepting a Brazilian ship in the Beagle Channel, disputed by Argentina and Chile.                                                                                                                                   |

| NAME         | 056                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Express forgiveness, pardon.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Usage Notes  | Use this event form to code verbal and nonverbal gestures of forgiveness and explicitly conciliatory actions or announcements. Formal pardons and amnesties of arrested persons, as well as the release or exchange of prisoners, should be coded as CAMEO 0841 instead.                                                                                                                                                                                                                                                                                                                                                           |
| Example      | A group of Yoruba leaders announced yesterday that they are willing to forgive President Olusegun Obasanjo and queue behind him for a second term.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| NAME         | 057                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Usage Notes  | Sign formal agreement Ratify, sign, finalize an agreement, treaty. This category excludes promises to sign or ratify agreements and treaties. Events should be coded under this category only when agreements are reportedly finalized or signed. This event code is typically reciprocal. Even when the agreement in question implies a formal commitment to boost material cooperation, provide aid, or yield in some way, the event of signing the agreement or treaty is still coded here since signing of an agreement or treaty represents diplomatic cooperation but does not guarantee implementation- whatever its terms. |
| Example      | Libyan leader Muammar Gaddafi and Bulgarian President Todor Zhivkov today signed a treaty of friendship and cooperation, the BTA reported. Two reciprocal events are coded with actors reversed. Czechoslovakia and China signed an agreement today to increase trade in 1983 by 50 percent compared with last year, the official Czechoslovak news agency Ceteka said today.                                                                                                                                                                                                                                                      |
| Example Note | Two reciprocal events are coded with actors reversed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |

## 2.6 ENGAGE IN MATERIAL COOPERATION

| NAME        | 060                                                                                                                                                                                                                                         |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Engage in material cooperation, not specified below                                                                                                                                                                                         |
| Usage Notes | Initiate, resume, improve, or expand material cooperation or exchange, not otherwise specified. This residual category is not coded except when distinctions among codes 061-064 cannot be made.                                            |
| Example     | Taliban ruled Afghanistan has been sharing expertise with the Liberation Tigers of Tamil Eelam according to a special report submitted to the Canadian Security Intelligence Service. Two reciprocal events are coded with actors reversed. |

| NAME         | Cooperate economically                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|--------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Initiate, resume, improve, or expand economic exchange or cooperation.                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Usage Notes  | Trade relations and other economic exchanges that are reciprocal in nature- event if the particular event in question cannot be coded as reciprocalseponduld be coded here. Unilateral and potentially altruistic provisions of economic aid should be coded as 071 instead.                                                                                                                                                                                                           |
| Example      | European foreign direct investment flows in Latin America and the Caribbean rose more than eightfold during the second half of the 1990s compared with the first half of that decade, according to a study presented in Paris by the Inter-American Development Bank. Two 061 events are coded due to the compound target.                                                                                                                                                             |
| Example Note | Cooperate militarily Initiate, resume, improve, or expand military exchange or cooperation.                                                                                                                                                                                                                                                                                                                                                                                            |
| Name         | Military exchanges such as joint military games and maneuvers should be coded here. Unilateral and potentially altruistic provisions of aid should be coded under 'Provide Aid' (07) instead.                                                                                                                                                                                                                                                                                          |
| Example      | French and Egyptian warships on Monday launched 10 days of war games in the Mediterranean Sea, expected to be joined later by Italian and German vessels, the French embassy said Monday. Two reciprocal events are coded with actors reversed.                                                                                                                                                                                                                                        |
| Example Note | Engage in judicial cooperation Initiate, resume, improve, or expand judicial cooperation. This code represents cooperation on judicial matters, such as extraditions and war crimes. Zambia extradited suspected British militant Haroon Rashid Aswad to Britain on Sunday, a senior Zambian government official said. Given that this is a cooperative code, the location where the subject is being extradited to-and not the identity of the suspect-should be coded as the target. |
| CAMEO        | Zambia extradited suspected British militant Haroon Rashid Aswad to Britain on Sunday, a senior Zambian government official said. Given that this is a cooperative code, the location where the subject is being extradited to-and not the identity of the suspect-should be coded as the target.                                                                                                                                                                                      |
| CAMEO        | Share intelligence or information Provide, share, or exchange intelligence or information. Voluntary exchanges or sharing of intelligence and other significant information should be coded here. Israeli intelligence officials have shared evidence with the U.S. about contacts                                                                                                                                                                                                     |
| Usage Notes  | between al Qaeda and senior members of Saddam Hussein's Ba'ath Party, according to governmental officials.                                                                                                                                                                                                                                                                                                                                                                             |

## 2.7 PROVIDE AID

| CAMEO       | 070                                                                                                                                                                                                                                                        |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | Provide aid, not specified below                                                                                                                                                                                                                           |
| Description | All provisions, extension of material aid, not otherwise specified.                                                                                                                                                                                        |
| Usage Notes | This residual category is not coded except when distinctions among codes 071-075 cannot be made. In order to be coded under this category, the leads must report the delivery of aids; promises to provide aid should be coded under category 033 instead. |
| Example     | Doctors from two American aid groups donated and personally delivered $50,000 worth of goods to Baghdad University Medical School, risking as much as 12 years in prison and $500,000 in fines.                                                            |
| CAMEO       | 071                                                                                                                                                                                                                                                        |
| Name        | Provide economic aid                                                                                                                                                                                                                                       |
| Description | Extend, provide monetary aid and financial guarantees, grants, gifts and credit.                                                                                                                                                                           |
| Usage Notes | The lead must report the delivery of such aid; promises to provide aid should be coded under 033 instead. Debt relief should also be coded as 071.                                                                                                         |
| Example     | The European Community on Monday gave the Ivory Coast 5.1 million dollars of aid for agricultural development projects.                                                                                                                                    |
| CAMEO       | 072                                                                                                                                                                                                                                                        |
| Name        | Provide military aid                                                                                                                                                                                                                                       |
| Description | Extend, provide military and police assistance including arms and personnel. The lead must report the delivery of such aid; promises to provide aid should be coded under category 033 instead.                                                            |
| Usage Notes | be coded under category 033 instead.                                                                                                                                                                                                                       |
| Example     | The United States continued to send arms to Pakistan last year, a State Department Spokesman said Wednesday.                                                                                                                                               |
| Example     | The United States is providing aerial photographs and other military intelligence to Macedonia which is preparing a major offensive against ethnic Albanian guerrillas, the Washington Post said Wednesday.                                                |

| NAME        | Provide humanitarian aid                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Extend, provide humanitarian aid, mainly in the form of emergency assistance.                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Usage Notes | This code refers to events such as provisions of shelter, food, medicine, and evacuation of victims. The lead must report the delivery of such aid; promises to provide aid should be coded under category 033. Note that provisions of peacekeeping or other military forces are coded as 074 instead.                                                                                                                                                                                                               |
| Example     | Swiss doctors handed over 700 kg of medicine to the Red Crescent in Bam, Iran, according to the Swiss Agency for Development and Cooperation. Benin opened its borders today to most West Africans ordered out of Nigeria as illegal aliens, but was still refusing admittance to Ghanaians, by far the biggest group involved, Benin police said. U.N. helicopters evacuated the wounded from the besieged Bosnian town of Gorazde on Friday.                                                                        |
| Example     | Provide military protection or peacekeeping                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Name        | Provide peacekeepers or other military forces for protection, extend or expand their mandates.                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Usage Notes | Code here reported deployment of forces; verbal promises and commitments to provide peacekeepers should be coded as 0334. Note that this event form is accompanied by the linked event 'Receive deployment of peacekeepers' (0861). The first deployment of NATO peacekeeping troops have arrived in Bosnia, Defense Secretary William Perry said. Two linked events-074 and 0861-should be coded with actors reversed.                                                                                               |
| Example     | Two linked events-074 and 0861-should be coded with actors reversed.                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| CAMEO       | 075 Grant asylum                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Name        | Provide, grant asylum to persons.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Usage Notes | Asylum is typically granted by states to persons in its territories (territorial asylum) and it constitutes a legal protection awarded to those persons against other states. Diplomatic asylum, protection typically accorded on the premises of an embassy, can also be granted and is similarly coded here. Not that 'Grant asylum' refers to a specific legal event type; informal provisions of shelter or opening of borders to masses of refugees should be coded as 'Provide humanitarian aid' (073) instead. |
| Example     | Peru has granted diplomatic asylum to five Panamanian army officers holed up in a diplomatic residence since last month's U.S. invasion, the Peruvian embassy said on Tuesday. Uganda has granted political asylum to 18 Zairean rebels who entered the country illegally two years ago and are wanted at home on treason charges, a United Nations official said on Friday.                                                                                                                                          |

## 2.8 YIELD

| NAME        | Yield, not specified below                                                                                                                                                                                                                                     |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | All yieldings, concessions not otherwise specified.                                                                                                                                                                                                            |
| Usage Notes | This residual category is not coded except when distinctions among codes 081-087 cannot be made. Not that all of the event forms under this category refer to reported yieldings and tot to future commitments, agreements, or promises.                       |
| Example     | Uganda said on Sunday it had paid compensation to 67 elderly British nationals, most of the Asians, for assets they lost when former dictator Idi Amin expelled them 18 years ago.                                                                             |
| NAME        | Ease administrative sanctions, not specified below                                                                                                                                                                                                             |
| Description | Relax or remove all administrative non-force sanctions and penalties, not otherwise specified.                                                                                                                                                                 |
| Usage Notes | This event category contains sub-forms for more detailed coding whenever possible.                                                                                                                                                                             |
| Example     | President Omar Hassan al-Bashir, following the partial peace deal, has taken several tentative steps to enhance political freedoms and promote an image of openness and tolerance in Sudan.                                                                    |
| NAME        | Ease restrictions on political freedoms                                                                                                                                                                                                                        |
| Description | Relax or remove administrative restrictions on fundamental political freedoms such as freedoms of speech, expression, and assembly.                                                                                                                            |
| Example     | The Latvian Constitutional Court cancelled restrictions on the use of the Russian language on national radio and television.                                                                                                                                   |
| NAME        | Ease ban on political parties or politicians                                                                                                                                                                                                                   |
| Description | Relax or remove administrative restrictions on the establishment or activities of political parties or certain politicians. The Ivory Coast's Supreme Court decided to allow candidate Alassane Ouat- tara to participate in the country's upcoming elections. |
| CAMEO       | 0813                                                                                                                                                                                                                                                           |
| Name        | Ease curfew                                                                                                                                                                                                                                                    |
| Description | Relax or remove regulations that require people to be off the streets at a given hour.                                                                                                                                                                         |
| Example     | Yugoslavia lifted a night curfew in Kosovo where 28 people have been killed in ethnic riots this year and the province was reported quiet on Sunday.                                                                                                           |
| Example     | President Omar El Bashir on Thursday shortened by one hour the nightly curfew imposed in Sudan after a June 30 coup toppled the civilian govern- ment.                                                                                                         |

| NAME        | Ease state of emergency or martial law                                                                                                                                                                                                                                                                                                                                                                                         |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Relax or remove emergency regulations that suspend certain given rights, or relax or remove temporary rule by military authorities.                                                                                                                                                                                                                                                                                            |
| Example     | Yugoslavia eased emergency measures on Wednesday in Kosovo province, the scene of ethnic violence last March, as authorities in Croatia cracked down on Serbian nationalists. Sudan's government on Sunday lifted a state of emergency in West Darfur State that was imposed six months ago after bloody tribal clashes there, Omdurman radio reported Sunday.                                                                 |
| CAMEO       | 082                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Name        | Ease political dissent                                                                                                                                                                                                                                                                                                                                                                                                         |
| Usage Notes | Use this code for concessions by opposition groups in form of ending or putting on hold demonstrations, protests, rallies, etc.                                                                                                                                                                                                                                                                                                |
| Example     | The Nigerian Union of Teachers (NUT), the umbrella union for primary school teachers, announced Thursday that it has called off a four-day strike after deliberations with the Nigerian government.                                                                                                                                                                                                                            |
| CAMEO       | 083                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Name        | Accede to requests or demands for political reform, not specified below                                                                                                                                                                                                                                                                                                                                                        |
| Usage Notes | Yield by instituting requested political changes. Note that this event type is different from 'Express intent to institute political reform' (034) as it involves the actual event of change-not just its promise. Just like military forms of yield, these could be voluntary concessions or involuntary surrenders. The Rwandan government on Thursday accepted demands from Hutu rebels that it initiate political reforms. |
| Example     | The Rwandan government on Thursday accepted demands from Hutu rebels                                                                                                                                                                                                                                                                                                                                                           |
| CAMEO       | 0831                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Name        | Accede to demands for change in leadership                                                                                                                                                                                                                                                                                                                                                                                     |
| Description | Yield by relinquishing political power.                                                                                                                                                                                                                                                                                                                                                                                        |
| Usage Notes | Use this code when source surrenders power after being challenged through legitimate institutional channels (e.g. elections) or other coercive strategies (e.g. military coups). The target can either be the challenger(s) or the country as a whole.                                                                                                                                                                         |
| Example     | Tuesday the Serbian parliament approved a "special law" recognizing victories by Zoran Djindjic's opposition coalition in November 17 municipal elections in 14 of the 18 most important Serbian cities, including Belgrade. Georgian President Eduard Shevardnadze resigned Sunday as the opposition threatened to storm his residence in Tbilisi.                                                                            |

| NAME        | 0832                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Yield by instituting demands for change in policy                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Usage Notes | Note the difference between policy and institutional change; the former can relate to any issue (economic, social, etc.) but it does not change the rules by which the political system functions. If another code within category 08 fits the policy in question more specifically, that code should take precedence (e.g. changing policy on economic sanctions should be coded as 085 instead). More often than not policies that fit under this particular code will be on domestic issues. As part of its fight to eradicate poverty, the governing Labour Party has introduced a legally-binding minimum rate of pay in Britain for the first time. |
| NAME        | 0833                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Description | Yield by establishing, providing, or respecting political, social, or other rights.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Usage Notes | Allowing repatriation of refugees should also be coded here. If another code within category 08 fits the rights in question more specifically, that code should take precedence (e.g. respecting property rights by returning confiscated property should be coded as 0842 instead). The Federal Minister for Interior Aftab Ahmad Khan Sherpao allowed opposition leader Maulana Fazl-ur-Rehman to bring out 'Shan-e-Mustafa (SAW)' Rally after an agreement on carrying out a violence free protest demonstration, according to the Pakistani Federal Secretary Interior.                                                                               |
| Example     | 0834                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Name        | Accede to demands for change in institutions, regime                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Description | Yield by undertaking major reforms that change how the political system functions. Changes from one type of a political system to another (e.g. from military dictatorship to multiparty democracy), as well as less comprehensive institutional changes that nevertheless modify the rules of the game (e.g. political party laws, electoral laws, powers and functions of different branches) are coded here.                                                                                                                                                                                                                                           |
| Example     | President Dos Sontas has reportedly conceded at last to demands from National Union for the Total Independence of Angola (UNITA) to overhaul the judiciary. Lt. Gen. Prosper Avril resigned yesterday to allow Haiti's first democratic elections to take place. The political change in this lead is more fundamental than leadership change given the mention of "first" democratic elections, which points to potential change in the overall political system (i.e. democratization).                                                                                                                                                                 |

| NAME        | Return, release, not specified below                                                                                                                                                                                                                                                        |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | All acts of releasing or returning not otherwise specified.                                                                                                                                                                                                                                 |
| Usage Notes | This category contains sub-forms for more detailed coding whenever possible.                                                                                                                                                                                                                |
| Example     | According to a zoo spokesperson Malaysian authorities have initiated the process of returning the four baby gorillas to Nigeria, amid speculations they were illegally captured in the wild.                                                                                                |
| CAMEO       | 0841                                                                                                                                                                                                                                                                                        |
| Name        | Return, release persons                                                                                                                                                                                                                                                                     |
| Description | Release people, including prisoners and hostages, from detention or arrest.                                                                                                                                                                                                                 |
| Usage Notes | Formal pardons, amnesties, commutations, and exchanges of prisoners should all be coded here.                                                                                                                                                                                               |
| Example     | Polish police today released the correspondent of the American news agency United Press International, who was detained for 23 hours and questioned in connection with an inquiry into alleged illegal activities.                                                                          |
| Example     | Bosnian Serb forces Tuesday let free six French UN peacekeepers held captive inside a UN armored personnel carrier since Friday, a UN spokesman said.                                                                                                                                       |
| CAMEO       | 0842                                                                                                                                                                                                                                                                                        |
| Name        | Return, release property                                                                                                                                                                                                                                                                    |
| Description | Return or release previously controlled, confiscated property, including land.                                                                                                                                                                                                              |
| Usage Notes | When confiscated property or other rights are not returned but compensation is provided instead, those incidents should be coded as 080.                                                                                                                                                    |
| Example     | French maritime authorities today release an impounded ship operated by the Greenpeace ecology movement, port officials said. An Egyptian court released a Lebanese millionaire's assets of nearly 19 million dollars on Saturday six years after they were frozen in a major bank scandal. |
| CAMEO       | 085                                                                                                                                                                                                                                                                                         |
| Name        | Ease economic sanction, boycott, or embargo                                                                                                                                                                                                                                                 |
| Description | Lift, relax, or lessen economic sanctions, boycott, embargoes, or penalties.                                                                                                                                                                                                                |
| Usage Notes | Use this event form to code state activities that imply easing of limitations to normal economic relations.                                                                                                                                                                                 |
| Example     | Germany on Wednesday lifted sanctions against gold from South Africa in recognition of the country's moves to abolish apartheid, a government spokesman said.                                                                                                                               |
| Example     | The United Arab Emirates (UAE) has lifted its boycott of trade in oil on Namibia, effective since March 31.                                                                                                                                                                                 |
| Example     | The European Union failed Wednesday to renew sanctions against Zimbabwe, with the fate of an EU-Africa summit scheduled for April hanging in the balance.                                                                                                                                   |

| NAME        | 086                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Allow entry of or intervention by international actors not further specified.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Usage Notes | Use the following sub-categories whenever possible. The types of international involvement covered in this category require physical access to territories under the source's control. Note that accepting international involvement in the form of mediation is coded under 04. The target should be the international actor whose involvement is allowed or received.                                                                                                                                                                                                                           |
| Example     | Kyrgyz Prime Minister Nikolai Tanaev received a mission of observers from the OSCE, informing them in detail on the economic situation of the country.                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| NAME        | Receive deployment of peacekeepers                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Usage Notes | Allow, receive peacekeeping forces in territories controlled by the source. Code here reported deployment of peacekeeping forces (with location of deployment as the source); mere promises or agreements by fighting parties or a country to accept deployment of peacekeeping forces in its territories should be coded as 0355, and commitments to provide peacekeepers should be coded as 0334. The target for an 084 event should be the actor providing the peacekeepers. Note that this event form is accompanied by the linked event 'Provide military protection or peacekeeping' (074). |
| Example     | A first patch of Bangladeshi peacekeeping troops arrived in Sierra Leone Tuesday, joining 12 unarmed military observers as the first element of an 800-strong Bangladeshi contingent due here, U.N. officials said.                                                                                                                                                                                                                                                                                                                                                                               |
| NAME        | Receive inspectors                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Description | Allow, receive inspectors in territories controlled by the source actor.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Usage Notes | Code here reported deployment or arrival of inspectors; mere promises or agreements to accept their deployment should be coded as 0355 instead. The target for an 085 event should be the inspectors or the country/agency providing them. This event form is typically accompanied by code under category 09.                                                                                                                                                                                                                                                                                    |
| Example     | The IAEA has dispatched inspectors to Esfahan Uranium Conversion Facilities (UCF) in central Iran to monitor resumption of peaceful nuclear work at the plant. Two linked events (0862 and 090) are coded with actors reversed.                                                                                                                                                                                                                                                                                                                                                                   |

| NAME        | 0863                                                                                                                                                                                                                                                                                                                                                                                     |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Allow access to, receive humanitarian agencies in territories controlled by the source actor.                                                                                                                                                                                                                                                                                            |
| Usage Notes | Mere promises to allow such access should be coded as 0355. Note that this event form is accompanied by the linked event 'Provide humanitarian aid' ( 073 ) if the target is the humanitarian agency; in some cases the target would be the particular area that is given access.                                                                                                        |
| Example     | Humanitarian access for the Darfur region has improved significantly since September as the Khartoum government tried to secure international favor. Uzbekistan finally opened the Friendship Bridge after four years to allow the delivery of 1,000 tons of grain and flour to Afghanistan, where millions of people are at risk of starvation as winter sets in, reports aid agencies. |
| CAMEO       | 087                                                                                                                                                                                                                                                                                                                                                                                      |
| Name        | De-escalate military engagement, not specified below                                                                                                                                                                                                                                                                                                                                     |
| Description | Concede militarily, stop fighting, or take measures to ease military conflict or tension not further specified.                                                                                                                                                                                                                                                                          |
| Usage Notes | Use sub-categories for more detailed coding whenever possible. Note that only real manifestations of de-escalation are coded here, expressions of intent to de-escalate are not.                                                                                                                                                                                                         |
| CAMEO       | 0871                                                                                                                                                                                                                                                                                                                                                                                     |
| Name        | Declare truce, ceasefire                                                                                                                                                                                                                                                                                                                                                                 |
| Description | Declare or observe truce or ceasefire to interrupt fighting.                                                                                                                                                                                                                                                                                                                             |
| Usage Notes | Although mere declarations of ceasefire, or agreements to commence a ceasefire, do not guarantee that military engagement is actually halted, they are still coded here. The target could be the location for the ceasefire or the opponent.                                                                                                                                             |
| Example     | The pro-Iranian Hizbollah (Party of God) group declared a unilateral ceasefire on Wednesday in south Lebanon after 12 days of battles with the Syrian- backed Amal militia.                                                                                                                                                                                                              |
| CAMEO       | 0872                                                                                                                                                                                                                                                                                                                                                                                     |
| Name        | Ease military blockade                                                                                                                                                                                                                                                                                                                                                                   |
| Description | Lessen or halt use of armed (military, police, or security) forces to seal off a territory to prevent exit or entry of goods and/or people.                                                                                                                                                                                                                                              |
| Example     | The Israeli army lifted Friday a day-old blockade on Palestinian lorryss passing through this crossing point between the Gaza Strip and the Jewish state, officials told AFP.                                                                                                                                                                                                            |

| CAMEO       | 0873                                                                                                                                                                                                                           |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | Demobilize armed forces                                                                                                                                                                                                        |
| Description | Hand over or otherwise reduce or eliminate arms, weapons; discharge soldiers or other armed personnel.                                                                                                                         |
| Usage Notes | The source actor for this event is the demobilizing party; the target is either the party against whom the source was formerly fighting or the actor to whom weaponry is turned in.                                            |
| Example     | One third of ethnic Albanian guerrillas operating in Macedonia have been demobilized since the August 13 peace accord between Macedonian and ethnic Albanian political parties, two rebel commanders told AFP by phone Sunday. |
| CAMEO       | 0874                                                                                                                                                                                                                           |
| Name        | Retreat or surrender militarily                                                                                                                                                                                                |
| Description | Retreat, withdraw, yield control of a location or territory by pulling out armed forces.                                                                                                                                       |
| Usage Notes | Note that the yielding should involve a comprehensive military disengagement, at least from a certain area of contention.                                                                                                      |
| Example     | Five hundred Ugandan rebels surrendered last week in the eastern town in Soroti followin a government offensive in the area, a local official said.                                                                            |
| Example     | The United States speeded up the withdrawal of some invasion forces from Panama on Wednesday, but defence officials cautioned that no deadline had been set for complete removal of the troops.                                |
| Example     | Bosnian Serbs said on Tuesday their forces had completed their withdrawal from the besieged Bosnian town of Gorazde.                                                                                                           |

## 2.9 INVESTIGATE

| CAMEO       | 090                                                                                                                                                                                                                                                                  |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | Investigate, not specified below                                                                                                                                                                                                                                     |
| Description | All non-covert investigations not otherwise specified.                                                                                                                                                                                                               |
| Usage Notes | This residual category is not coded except when distinctions among codes 091-094 cannot be made. Also note that category 09 should be used only when investigations are being or have been carried out. Investigation of historical cases should also be coded here. |
| Example     | The United Nations has sent 21 military and civilian personnel to Yugoslavia on Wednesday to investigate the feasibility of a 10,000-member peacekeeping force, a U.N. spokesman said on Monday.                                                                     |

| NAME        | Investigate crime, corruption                                                                                                                                                                                                                                                                                                                             |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Question or inquire criminal (theft, killing, etc) or corruption cases.                                                                                                                                                                                                                                                                                   |
| Example     | Judge Alejandro Rivera opened fraud investigations against 28 Chilean gov- ernment officials suspected of taking kickbacks, the court said Friday.                                                                                                                                                                                                        |
| Example     | A US national has been put under investigation in Italy for her possible role in rioting during a G8 summit in Genoa last month, Ansa news agency reported.                                                                                                                                                                                               |
| NAME        | Inquire or search into human rights abuses such as rape, torture, targeted assassinations, and violations of basic freedoms.                                                                                                                                                                                                                              |
| Usage Notes | Investigations of war crimes are coded as 094 instead. Alleged or potential perpetrators should be coded as targets.                                                                                                                                                                                                                                      |
| Example     | Members of the Association of African Jurists, a body linked to the Organi- zation of African Unity, investigated welfare of nearly 2,000 Libyans, some of whom have been held as long as seven years.                                                                                                                                                    |
| Example     | Israel's high court opened a landmark hearing Wednesday into the legality of secret interrogation techniques used against Palestinian detainees.                                                                                                                                                                                                          |
| NAME        | Inquire military action                                                                                                                                                                                                                                                                                                                                   |
| Description | Inquire or search into military activities such as violations of ceasefire, seizures, and invasions. If military actions in question involve potential human rights violations or war crimes specifically, code them as 092 or 094 instead. The perpetrator of the questionable military action should be coded as the target.                            |
| Example     | The Ceasefire Violations Committee (CFVC) has completed its investigation into an allegation by the Liberian Peace Council (LPC) that the NPFL had taken over the city of Greenville.                                                                                                                                                                     |
| NAME        | Inquire or investigate potential war crimes or look into allegations of war crimes. If the question surrounding a military action is not specified to be potential war crimes, 093 should be used instead. The perpetrator of the questionable military action should be coded as the target.                                                             |
| Example     | Serb civilians and prisoners and will bring suspects to trial, a Croatian official said. Serbian military police have launched an investigation into alleged crimes committed by Croat forces against ethnic Serb civilians and Montenegrin prisoners of war during the 1991-1995 Serbo-Croatian conflict, the newspaper Jutarnji list reported Thursday. |

## 2.10 DEMAND

| CAMEO       | 100                                                                                                                                                                                                                                                                                                                                                                                             |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | Demand, not specified below                                                                                                                                                                                                                                                                                                                                                                     |
| Description | All demands and orders not otherwise specified.                                                                                                                                                                                                                                                                                                                                                 |
| Usage Notes | This residual category is not coded except when distinctions among codes 101-108 cannot be made. Note that demands are stronger or more forceful and potentially carry more serious repercussions-although not as much as threats-than simple appeals. We rely primarily on the language used by reporters to make this distinction. All demands are verbal acts.                               |
| Example     | Poland's parliament has demanded an immediate admission by Moscow that Soviet NKVD security forces murdered more than 15,000 captive Polish off-ficers during World War Two.                                                                                                                                                                                                                    |
| CAMEO       | 101                                                                                                                                                                                                                                                                                                                                                                                             |
| Name        | Demand material cooperation, not specified below                                                                                                                                                                                                                                                                                                                                                |
| Description | Require, demand that target engages in some form of material exchange.                                                                                                                                                                                                                                                                                                                          |
| Usage Notes | Use the following sub-categories whenever possible. Demands for judicial co- operation, such as extradition of criminals, or compliance with requirements of an investigation are coded here.                                                                                                                                                                                                   |
| Example     | French President Jacques Chirac issued a stern reminder Saturday to Iraq that it must cooperate fully with UN inspectors probing suspect sites for weapons of mass destruction. An Argentine judge has ordered former president Carlos Mene m to appear October 16 for questioning in an investigation of illegal arms sales to Croatia and Ecuador in the 1990s, court sources said Wednesday. |
| CAMEO       | 1011                                                                                                                                                                                                                                                                                                                                                                                            |
| Name        | Demand economic cooperation                                                                                                                                                                                                                                                                                                                                                                     |
| Description | Require, demand that target engages in economic exchange or expands such ties.                                                                                                                                                                                                                                                                                                                  |
| Usage Notes | Use this code for demands for economic activities such as trade and investment. Demands for provision of economic aid-not mutual exchange-are coded as 1031 instead.                                                                                                                                                                                                                            |
| Example     | The Bush administration declared Tuesday that China must drop barriers to U.S. exports or face tariff penalties for maintaining unfair trade practices.                                                                                                                                                                                                                                         |

| NAME         | 1012 Demand military cooperation                                                                                                                                                                                                                                                                                        |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Use this code for demands that target engages in or expands military relations.                                                                                                                                                                                                                                         |
| Usage Notes  | as through joint exercises or weapon sales. Demands for provision of military aid-not mutual exchange-are coded as 1032 instead.                                                                                                                                                                                        |
| Example      | The PRC on Tuesday demanded that the US cancel plans to sell air-tosurface anti-tank weapons to Taiwan to avoid "new damage" to US-PRC relations.                                                                                                                                                                       |
| Example Note | While the requested policy does not directly involve material exchange between the source and the target, the former is clearly demanding cooperation on military issues.                                                                                                                                               |
| CAMEO        | 1013 Demand judicial cooperation                                                                                                                                                                                                                                                                                        |
| Name         | Require, demand that target engages in or expands cooperation in judicial matters.                                                                                                                                                                                                                                      |
| Usage Notes  | Use this code for demands that target engages in judicial cooperation, such as through extrading wanted individuals.                                                                                                                                                                                                    |
| Example      | A senior British minister reiterated that Libya must hand over alleged bombers of the U.S. airliner as he embarked on a trip to North Africa to seek Arab support for the demand.                                                                                                                                       |
| CAMEO        | 1014 Demand intelligence cooperation                                                                                                                                                                                                                                                                                    |
| Name         | Require, demand that target exchanges intelligence or information.                                                                                                                                                                                                                                                      |
| Usage Notes  | Use this code for demands that target engages in intelligence cooperation, including but not limited to the exchange of information in security matters. The rebel Kurdistan Workers' Party issued a declaration demanding that the Turkish government provide information on the safety of its leader Abdullah Ocalan. |
| CAMEO        | 102 Demand for diplomatic cooperation (such as policy support)                                                                                                                                                                                                                                                          |
| Name         | Require, demand expansion of diplomatic ties or cooperation. This code refers to demands for expanded diplomatic ties and non-tangible support on particular policies. Demands for more specific forms of diplomacy, such as mediation and negotiation are coded elsewhere within category 10.                          |
| Usage Notes  | 10. Kosovo Municipality Association (AKK) officials demanded support from the Kosovo Assembly in regaining control over the properties that belonged to them before.                                                                                                                                                    |
| Example      | Greece bluntly demanded that its European Community partners refuse to recognize the Former Yugoslav Republic of Macedonia, on Greece's northern border, as long as it keeps that name.                                                                                                                                 |
| Example      | Palestinian officials demanded Friday that the United States match the European Union's support for Palestinian statehood.                                                                                                                                                                                              |

| NAME        | Demand material aid, not specified below                                                                                                                                                                                                                                                                             |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Require, demand provision of material assistance not otherwise specified.                                                                                                                                                                                                                                            |
| Usage Notes | This category contains sub-forms for more detailed coding whenever possible. The source could be demanding aid for itself or on behalf of a third party; in either case, the actor who is expected to provide assistance should be coded as the target.                                                              |
| Example     | The Third World Water Forum concluded on Saturday that the US and other developed nations must allocate greater financial resources to help with the battle against the global water and sanitation crisis.                                                                                                          |
| NAME        | Demand economic aid                                                                                                                                                                                                                                                                                                  |
| Usage Notes | This event form is typically, although not exclusively, a verbal act. Demands for loans or debt relief are also coded here. Demands for reciprocal economic exchange, such as trade, should be coded as 1011 instead.                                                                                                |
| Example     | According to reports the UK is pushing hard for the US support its debt relief plan to tackle poverty in Africa.                                                                                                                                                                                                     |
| NAME        | Demand military aid                                                                                                                                                                                                                                                                                                  |
| Usage Notes | Note that demands for military security and deployment of peacekeepers are coded as 1034 instead.                                                                                                                                                                                                                    |
| NAME        | Demand humanitarian aid                                                                                                                                                                                                                                                                                              |
| Usage Notes | Require, demand provision of humanitarian aid. Demands by refugees to be let into the territories of other countries (which should be coded as targets) and asylum demands all fit here. These are not necessarily verbal acts; refugees could be actively seeking shelter or refuge in target countries or regions. |
| Example     | Some 800,000 Iraqi Kurds sought refuge in Germany last month.                                                                                                                                                                                                                                                        |

| NAME         | 1034                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|--------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Demand military protection or peacekeeping                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Usage Notes  | The source that demands peacekeepers could demand that for itself or on                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Example      | Ethnic Albanians in south Serbia are demanding a U.N. military presence to protect them against a heavily armed ruling Serb minority and prevent a Bosnia-style civil war, but some foreign monitors are skeptical.                                                                                                                                                                                                                                                                                                                    |
| Example      | The Red Cross operating in Iraq said US and British forces must ensure security to allow emergency water, food, and medical supplies to reach the needy.                                                                                                                                                                                                                                                                                                                                                                               |
| Example Note | Two events are coded due to the compound target.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| NAME         | Demand political reform, not specified below                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Description  | Require, demand political change not otherwise specified.                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Usage Notes  | This event form refers to verbal and non-threatening appeals. Demands that take the form of demonstrations, protests, etc. are coded under category 14 instead. Source actors can be local citizens as well as international actors; they could be making the appeal on their own behalf or on behalf of others. Note that when the requested reform clearly constitutes some form of concession or yielding by the target, such as the easing of administrative sanctions, a more appropriate "Demand" code might be found under 105. |
| Example      | At the end of a seminar on reform, around 100 Arab intellectuals and activists published a declaration demanding wide-ranging political changes in the Arab world.                                                                                                                                                                                                                                                                                                                                                                     |
| NAME         | Demand leadership change                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Description  | Require, demand change in leadership or power.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Usage Notes  | This event form refers to verbal and non-threatening appeals. Demands that take the form of demonstrations, protests, etc. are coded under category 14 instead. Note that even though demands for the target to resign or relinquish power are forms of yielding, they are still coded here. Also code demands for elections here (unless they are first-time elections and hence constitute major institutional change).                                                                                                              |
| Example      | Sunnis have demanded that control of the Interior Ministry be taken away from Shiite religious parties in the next government.                                                                                                                                                                                                                                                                                                                                                                                                         |
| Example      | Rwandan rebels demanded the removal of President Juvenal Habyariman and his ruling party at the fourth round of talks aimed at ending a 23-month civil war.                                                                                                                                                                                                                                                                                                                                                                            |
| Example      | Former Socialist prime minister Andreas Papandreou demanded immediate elections after a special court cleared him of all charges in Greece's biggest corruption trial this century.                                                                                                                                                                                                                                                                                                                                                    |

| NAME        | 1042                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Demand policy change                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Usage Notes | This event form refers to verbal and non-threatening demands. Demands that take the form of demonstrations, protests, etc. are coded under category 14 instead. Just like the source actor, the policy in question can also be domestic or international in nature. If it is clear from the lead that by demanding certain policy changes the source is in fact demanding that the target yield or concede, the event might be better coded under 105 (e.g. demands for military withdrawal should be coded as 1056). Opposition groups in Zimbabwe are demanding that President Mugabe abandon his controversial policy of land confiscations. |
| Example     | Opposition groups in Zimbabwe are demanding that President Mugabe abandon his controversial policy of land confiscations.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| NAME        | 1043                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Description | Demand rights                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Usage Notes | This event form refers to verbal and non-threatening demands. Demands that take the form of demonstrations, protests, etc. are coded under category 14 instead. If it is clear from the lead that by demanding certain rights the source is in fact demanding that the target yield or concede, the event might be better coded under 105. Demands for provision of compensation for previously violated rights, for instance, are coded as 105.                                                                                                                                                                                                |
| Example     | The main Hutu rebel group, Forces for Defence of Democracy (FDD), insisted on its demands that Burundi's government grant the Hutu majority more rights.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| NAME        | 1044                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Description | Demand change in institutions, regime                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Usage Notes | This event form refers to verbal and non-threatening demands. Demands that take the form of demonstrations, protests, etc. are coded under category 14 instead. Institutional change is different from policy change in that the former directly alters the rules of the game. Demands for fundamental changes in the political system (e.g. democratization) as well as more limited institutional changes (e.g. changing electoral law) are coded here.                                                                                                                                                                                       |
| Example     | Rwandan rebels announced that President Kagame and his Rwandan Patriotic Front must agree to major constitutional changes before they demobilize. The Albanians of southern Serbia are demanding political and territorial autonomy from Serbian authorities.                                                                                                                                                                                                                                                                                                                                                                                   |

| NAME        | 105 Demand that target yield, not specified below                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Require, demand that target yields or concedes, not otherwise specified.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Usage Notes | This event form is typically, although not exclusively, a verbal act. The source for this event type may or may not be one of the adversaries; a third party could also be demanding that one or more of the parties in conflict (who are coded as targets) to yield. When a threat is attached to a demand for yielding, the appropriate code under category 13 should be used instead. Also, if accompanied by some form of protest activity, codes under category 14 should be used. When yielding actually takes place, use the appropriate code under category 08. The United States on Thursday demanded that the Democratic People's Republic of Korea (DPRK) forsake its nuclear program. |
| Example     | Because no military engagement has yet occurred, this default code is used instead of 1056.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| CAMEO       | 1051                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Name        | Demand easing of administrative sanctions                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Description | Require, demand that target relaxes administrative restrictions.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Usage Notes | Use this code when a government is pushed to undertake some political changes that clearly constitute some form of concession or yielding, such as relaxing or removing bans, curfews, or other restrictions that are already in place. Demands that take the form of demonstrations, protests, etc. are coded under category 14 instead. Human rights organization Amnesty International demanded that the Su- danese government end curbs on press freedom. The International Labor Office (ILO) reiterated its demand today that Israel ease restrictions on the movement of Palestinian workers.                                                                                              |
| CAMEO       | 1052                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Name        | Demand easing of political dissent                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Usage Notes | Use this code for demands that the target stop engaging in protests, demonstrations, strikes, etc. Note that this code refers exclusively to verbal de- mands; if the source actively seeks to stop activities through repressive measures, 175 is used instead.                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Example     | Iranian authorities have been pressuring workers of the United Bus Company of Tehran (Sharekat-e Vahed) to cancel the strike they have been planning for better pay and working conditions.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| CAMEO       | 1053                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Name        | Demand release of persons or property                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Description | Require, demand that target releases persons or property.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Usage Notes | Use this code for demands that the target release prisoners, hostages, and any confiscated property.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Example     | Russia said on Tuesday that Sudan must return a Mi-26 helicopter that was captured by the Sudanese authorities last week.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |

| NAME        | 1054                                                                                                                                                                                                                                                                                                             |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Demand easing of economic sanctions, boycott, or embargo                                                                                                                                                                                                                                                         |
| Usage Notes | Use this code only for economic sanctions, boycotts, or embargoes. The 106th Inter-Parliamentary Union Conference stressed the obligation of the international community to take immediate action to lift embargoes and other sanctions which have negatively affected children in different parts of the world. |
| CAMEO       | 1055                                                                                                                                                                                                                                                                                                             |
| Name        | Demand to allow international involvement (non-mediation)                                                                                                                                                                                                                                                        |
| Description | Require, demand that target allow access to international actors, such as observers, humanitarian agencies, and peacekeeping forces. Demands for adversaries to allow mediation are coded as 108 instead. Kenzo Oshima, the United Nations Emergency Relief Coordinator, de-                                     |
| Usage Notes | freedom of movement necessary for discharging their mandate.                                                                                                                                                                                                                                                     |
| CAMEO       | 1056                                                                                                                                                                                                                                                                                                             |
| Name        | Demand de-escalation of military engagement                                                                                                                                                                                                                                                                      |
| Description | Require, demand that target stops fighting or takes measures to ease military conflict or tension. Use this code for demands for ceasefire, military withdrawals, and demobilization.                                                                                                                            |
| Usage Notes | Washington along with its allies demanded that Hamas renounce its armed struggle against Israel. European Community foreign ministers demanded the withdrawal of Y-                                                                                                                                              |
| Example     | goslav federal forces from Bosnia-Herzogovina on Monday calling them an occupying army, diplomats quoted an EC declaration as saying.                                                                                                                                                                            |
| Example     | Bosnian Serbs demanded a truce with Moslem forces in east Bosnia before allowing U.N. aid conveys to feed starving Moslem civilians in the region.                                                                                                                                                               |
| CAMEO       | 106                                                                                                                                                                                                                                                                                                              |
| Name        | Demand meeting, negotiation                                                                                                                                                                                                                                                                                      |
| Description | Require, order party(ies) to meet, negotiate. This event form can be initiated by either the adversaries or other third parties.                                                                                                                                                                                 |
| Usage Notes | Yugoslavia on Tuesday demanded a meeting of the U.N. Security Council to discuss Croatia's military advance into the Serb-held Krajin a region, describing it as "a serious challenge to the world community."                                                                                                   |

| NAME         | 107 Demand settling of dispute                                                                                                                                                                                                                                                                                               |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Order parties to a conflict to reach a settlement, agreement, or resolution of conflict.                                                                                                                                                                                                                                     |
| Usage Notes  | This event form is typically, although not exclusively, a verbal act. Note that the source for this event cannot be the adversaries themselves. When one or more parties to a conflict call for ending the conflict, that is taken to be an expression of intent on the part of that source actor and is thus coded as GLYPH |
| Example      | Jack Straw said on Friday that the Sudanese government and the rebels in Darfur must reach an agreement that stops the conflict for good before developmental assistance to the region is released. Because of the compound target, two separate events are coded.                                                           |
| Example Note | 108                                                                                                                                                                                                                                                                                                                          |
| NAME         | Demand mediation                                                                                                                                                                                                                                                                                                             |
| Description  | Require or demand that a third party mediates a conflict or that adversaries accept mediation of another party.                                                                                                                                                                                                              |
| Usage Notes  | This event form is a verbal act. It specifically refers to demands by actors other than potential mediators; either the adversaries or a prospective mediator can be coded as the target.                                                                                                                                    |
| Example      | Egyptian President Hosni Mubarak said here Wednesday that the US must be ready to mediate between Israelis and Palestinians as soon as the Israeli elections of January GLYPH                                                                                                                                                |

## 2.11 DISAPPROVE

| NAME        | 110 Disapprove, not specified below                                                                                                        |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Express disapprovals, objections, and complaints not otherwise specified.                                                                  |
| Usage Notes | This residual category is not coded except when distinctions among codes 111-116 cannot be made. Disapprovals are typically verbal events. |
| Example     | On Tuesday, Nigerian junior foreign minister Dubem Oniya summoned NigerGLYPH                                                               |
| NAME        | Criticize or denounce                                                                                                                      |
| Description | Condemn, decry a policy or an action; criticize, defame, denigrate responsi- ble parties.                                                  |
| Example     | Albania on Friday denounced as an ugly crime YugoslaviaGLYPH                                                                               |

| NAME        | Accuse, not specified below                                                                                                                                                                                                                                                                                                      |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Charge, blame, incriminate for allegations not otherwise specified.                                                                                                                                                                                                                                                              |
| Usage Notes | This event category contains sub-forms for more detailed coding whenever possible. Note that events coded under 112 are allegation made by actors and do not in any way imply that the alleged events have taken place .                                                                                                         |
| Example     | Zimbabwean Prime Minister Robert Mugabe today accused the United States of restoring the blackmail in the negotiations on independence for Namibia.                                                                                                                                                                              |
| NAME        | ACCUSE of crime, corruption                                                                                                                                                                                                                                                                                                      |
| Description | Allege, charge the target with, or blame for engaging in crime or corruption. Ousted president Jean-Bertrand Aristide has been accused of misusing up to US $50 million ( $73 million) in public funds, much of it believed to have been embezzled, by current Haitian government officials.                                     |
| NAME        | ACCUSE of human rights abuses                                                                                                                                                                                                                                                                                                    |
| Description | Allege, charge the target with, or blame for human rights violations, such as arbitrary detentions for prosecutions, torture, and slavery. Human rights watchdog Amnesty International accused the United States of violating human rights, ignoring international law and sending a "permissive signal to abusive governments". |
| NAME        | ACCUSE of aggression                                                                                                                                                                                                                                                                                                             |
| Description | Allege, charge the target with, or blame for initiating hostilities or engaging in questionable or unjustifiable military actions such as violations of ceasefire. If the nature of the military action in question relates to human rights abuses or war crimes, they should be coded elsewhere within this category.           |
| Example     | The Sudanese government has accused Darfur rebels of violating a month- old ceasefire, a member of the Chadian team trying to broker a peace pact has said.                                                                                                                                                                      |
| Example     | Palestinians blamed Israel for the bombing of Raed Karmi in the West Bank City of Tulkarm, which has set off a renewed wave of violence.                                                                                                                                                                                         |
| NAME        | ACCUSE of war crimes                                                                                                                                                                                                                                                                                                             |
| Description | Allege, charge the target with, or blame for participation in war crimes/ Kosovo's prime minister has been indicted by the U.N. war crimes court for his alleged part in atrocities during the fight against Serb forces and will resign.                                                                                        |

| NAME        | 1125                                                                                                                                                                                                                                                                                                                                       |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Allege, charge the target with, or blame for spying, espionage, or treason.                                                                                                                                                                                                                                                                |
| Example     | A Christian missionary from Calgary was arrested in Lebanon for collaborating with Israel, according to the Canadian Press.                                                                                                                                                                                                                |
| Example     | Nigerian authorities jailed 52 members of the banned Movement for the Actualization of the Sovereign State of Biafra (MASSOB) on allegations of treason for playing in a youth football tournament in Lagos.                                                                                                                               |
| CAMEO       | 113                                                                                                                                                                                                                                                                                                                                        |
| Name        | Rally opposition against                                                                                                                                                                                                                                                                                                                   |
| Usage Notes | This event form is typically, although not exclusively, a verbal act. Use this event form to code instances where one party (the source) solicits third parties to express disapproval of, protest against, or punish another party (the target). Note that only diplomatic solicitations-not military mobilizations-should be coded here. |
| Example     | An official Syrian newspaper called Thursday on Arabs to unite and "mobilize" against Israeli right-winger Ariel Sharon, who has vowed not to return the Golan Heights to Syria if he is elected prime minister February 4.                                                                                                                |
| Example     | Archbishop Desmond Tutu on Sunday called for sanctions against Nigeria in the wake of the execution of Ken Saro-Wiwa.                                                                                                                                                                                                                      |
| CAMEO       | 114                                                                                                                                                                                                                                                                                                                                        |
| Name        | Complain officially                                                                                                                                                                                                                                                                                                                        |
| Description | Written and institutionalized protests, appeals, and all petition drives and recalls.                                                                                                                                                                                                                                                      |
| Example     | Yugoslavia lodged an official protest with Albania today, charging its neigh- bor with supporting dissidents here in what is said was tantamount to inciting revolution.                                                                                                                                                                   |
| Example     | Lebanon complained to the United Nations on Tuesday over two Israeli air raids last Friday in which it said 20 people were killed or wounded.                                                                                                                                                                                              |
| CAMEO       | 115                                                                                                                                                                                                                                                                                                                                        |
| Name        | Bring lawsuit against                                                                                                                                                                                                                                                                                                                      |
| Description | Sue, file civil or criminal lawsuit at domestic or international courts.                                                                                                                                                                                                                                                                   |
| Usage Notes | Source must be the plaintiff or the state, and target must be the defendant.                                                                                                                                                                                                                                                               |
| Example     | A Saudi businessman is suing the United States for damages to his pharmaceutical plant which were caused by a missile attack in August, his American lawyer said.                                                                                                                                                                          |

| NAME        | 116                                                                                                                                                                                                                                                                                                         |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Find guilty or liable (legally)                                                                                                                                                                                                                                                                             |
| Usage Notes | Source must be the court in question, which could be domestic or interna- tional, and target must be the defendant. This event form refers typically to rulings against non-individuals, where imprisonment is not an issue. When individuals are found guilty and are therefore detained, use 173 instead. |
| Example     | A European court convicted Turkey of "inhuman acts" Thursday for de- stroying the home of a Kurdish citizen in the country's southeast.                                                                                                                                                                     |

## 2.12 REJECT

| Name        | 120                                                                                                                                                                                                                                                                                                                    |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | All rejections and refusals not otherwise specified.                                                                                                                                                                                                                                                                   |
| Usage Notes | This residual category is not coded except when distinctions among codes 121-129 cannot be made. All rejections coded under this category should imply refusals to cooperate or yield in some way.                                                                                                                     |
| Example     | The Palestinians reject proposed Israeli changes to the Wye River land-for- security deal, chief Palestinian negotiator Saeb Erakat said.                                                                                                                                                                              |
| Name        | 121                                                                                                                                                                                                                                                                                                                    |
| Description | Refuse to engage in or expand material exchange.                                                                                                                                                                                                                                                                       |
| Usage Notes | This category contains sub-forms for more detailed coding whenever possible. Refusals to provide unilateral material assistance-not mutual exchangere- coded as 122 instead. Note the difference between refusing to establish or expand material cooperation and reducing or eliminating existing ties (category 16). |
| Example     | Yemen has rejected a U.S. request to interrogate detainees held after the escape of 23 al-Qaida prisoners, a security official said Tuesday.                                                                                                                                                                           |
| Name        | 1211                                                                                                                                                                                                                                                                                                                   |
| Description | Refuse to engage in or expand economic ties.                                                                                                                                                                                                                                                                           |
| Usage Notes | Use this code for rejections of mutual economic exchange, such as trade and investment; rejection to provide financial aid (or cancel debt) is coded as 1221 instead.                                                                                                                                                  |
| Example     | Bangladesh has once again outright rejected an Indian proposal for signing Free Trade Agreement (FTA) with her, urging the counterpart to sign the proposed South Asia Free Trade Agreement (SAFTA) instead.                                                                                                           |

| NAME        | 1212                                                                                                                                                                         |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Refuse to engage in or expand military ties.                                                                                                                                 |
| Usage Notes | Use this code for rejections of mutual military exchange; rejection to provide military aid is coded as 1222 instead.                                                        |
| Example     | South Korea has rejected North Korea's consistent demand to sever a decades-long military alliance with Washington, which keeps troops here under a mutual defense pact.     |
| CAMEO       | 1213                                                                                                                                                                         |
| Name        | Reject judicial cooperation                                                                                                                                                  |
| Description | Refuse to engage in or expand cooperation in judicial matters.                                                                                                               |
| Usage Notes | Use this code when the source actor refuses to cooperate in extraditions or other matters pertaining to legal proceedings.                                                   |
| Example     | Yugoslavia on Thursday flatly rejected an Australian ultimatum to handover a guard involved in a shooting in front of the Yugoslav consulate in Sydney.                      |
| CAMEO       | 1214                                                                                                                                                                         |
| Name        | Reject intelligence cooperation                                                                                                                                              |
| Description | Refuse to engage in or expand cooperation in intelligence or information sharing.                                                                                            |
| Usage Notes | Use this code when the source actor refuses to investigate or share information.                                                                                             |
| Example     | The UN on Tuesday imposed a de facto information blackout on the withdrawal, collection and monitoring of heavy weapons around Sarajevo.                                     |
| CAMEO       | 122                                                                                                                                                                          |
| Name        | Reject request or demand for material aid, not specified below                                                                                                               |
| Description | Refuse to extend material aid not otherwise specified.                                                                                                                       |
| Usage Notes | Use this event form to code refusals to provide material assistance. Use sub-categories whenever possible.                                                                   |
| CAMEO       | 1221                                                                                                                                                                         |
| Name        | Reject request for economic aid                                                                                                                                              |
| Description | Refuse to extend financial assistance.                                                                                                                                       |
| Example     | Bonn rejected recent calls by East Germany's Communist rulers for immediate economic aid, saying it was withholding it until a democratically-elected government takes over. |
| CAMEO       | 1222                                                                                                                                                                         |
| Name        | Reject request for military aid                                                                                                                                              |
| Description | Refuse to extend military assistance.                                                                                                                                        |
| Example     | The Turkish government has refused to commit to any direct assistance to the US-led war against Iraq, citing domestic opposition.                                            |

| NAME        | 1223                                                                                                                                                                                                                                   |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Refuse to extend humanitarian assistance.                                                                                                                                                                                              |
| Usage Notes | Refusals to provide shelter or refuge should also be coded here. When source                                                                                                                                                           |
| Example     | refuse to grant humanitarian agencies access (instead of refusing to provide                                                                                                                                                           |
| CAMEO       | 1224                                                                                                                                                                                                                                   |
| Name        | Refuse to provide peacekeeping forces or other form of military protection.                                                                                                                                                            |
| Description | Refusals by prospective providers of protection and peacekeeping should be                                                                                                                                                             |
| Usage Notes | coded here; refusals by adversaries to grant access to peacekeepers should                                                                                                                                                             |
| Example     | be deployed in East Timor.                                                                                                                                                                                                             |
| CAMEO       | Pakistan, a key U.S. ally in the war against terrorism, has refused to deploy peacekeepers in Iraq and has urged its citizens to avoid coming here.                                                                                    |
| Name        | Refuse to institute political change not otherwise specified.                                                                                                                                                                          |
| Description | Refuse to institute political change not otherwise specified.                                                                                                                                                                          |
| Usage Notes | If the reform in question clearly constitutes some form of concession or yielding by the source, such as the easing of existing administrative sanctions, a more appropriate code might be found under 124 ('Refuse to yield'). Actors |
| Example     | requested the demand or those (the country or the people) that will be affected by the rejection should be coded as target depending on availability of information in the lead.                                                       |
| CAMEO       | The US on Thursday rejected calls by Kofi Annan, UN secretary-general, to adopt far-reaching United Nations reforms as a comprehensive package.                                                                                        |
| Name        | Refuse to change leadership or relinquish power.                                                                                                                                                                                       |
| Description | Refuse to change leadership or relinquish power.                                                                                                                                                                                       |
| Usage Notes | Refuse to open the way for change in leadership, are coded here. Note that while refusals to undertake other forms of yielding are coded under 124,                                                                                    |
| Example     | Vice-President Moody Awori has declined to resign despite growing pressure by the Kenya Anti-Corruption Commision after he was implicated in a major scandal.                                                                          |

| Name        | 1232                                                                                                                                                                                                                                                      |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Refuse to change a given policy.                                                                                                                                                                                                                          |
| Usage Notes | Use this code for refusals to acquiesce to demands for policy change- political, economic, military, social, or otherwise. If the policy change in question clearly represents a form of yielding, the appropriate code under 124 should be used instead. |
| CAMEO       | 1233                                                                                                                                                                                                                                                      |
| Name        | Refuse to provide or respect social, political, economic or other rights and freedoms. If it is clear from the lead that by rejecting certain rights the source is in fact refusing to yield or concede, the event might be better coded under 124.       |
| Usage Notes | Ankara's Çankaya district administration has denied land allocation for the construction of an Alevite temple, Cemevi, in the district.                                                                                                                   |
| CAMEO       | 1234                                                                                                                                                                                                                                                      |
| Name        | Refuse to make fundamental political changes, such as moving from one type of a political system to another and reforming political institutions or key laws.                                                                                             |
| Usage Notes | Note the difference between institutional/regime changes and policy reforms. In what has been described as a policy u-turn, President Levy Mwanawasa has reneged on his commitment to the Zambian people for holding elections under a new constitution.  |
| CAMEO       | 124                                                                                                                                                                                                                                                       |
| Name        | Refuse to yield, not specified below                                                                                                                                                                                                                      |
| Description | Reject requests, refuse, or decline to yield not otherwise specified. This category contains sub-forms for more detailed coding whenever possible.                                                                                                        |
| CAMEO       | 1241                                                                                                                                                                                                                                                      |
| Name        | Refuse to ease administrative sanctions                                                                                                                                                                                                                   |
| Description | Reject requests, refuse or decline to ease administrative sanctions, such as censorship, curfew, state of emergency, and martial law.                                                                                                                     |
| Example     | Despite warnings of starvation by humanitarian agencies, the Israeli government is refusing to lift the curfew on Palestinians living in the West Bank and Gaza.                                                                                          |
| CAMEO       | 1242                                                                                                                                                                                                                                                      |
| Name        | Refuse to ease popular dissent Reject requests, refuse, or decline to reduce or stop political protest activities, such as demonstrations and rallies.                                                                                                    |
| Example     | Around 1,800 of 2,200 Serbian teachers will not end their strike unless their demands for wage increases are met by textcolorblueBelgrade, a union official announced after three weeks of striking.                                                      |

| CAMEO       | 1243                                                                                                                                                                                                                                                |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | Refuse to release persons or property                                                                                                                                                                                                               |
| Description | Reject requests, refuse, or decline to release or return persons or property.                                                                                                                                                                       |
| Usage Notes | Refusals to release or exchange prisoners and hostages, as well as to return previously confiscated properties, are coded here. The U.S. said it would not meet hostage-takers demands to release prisoners in Iraq, including a number of females. |
| Example     | In an ideal scenario, the identity of the hostage-takers would have been codeable here.                                                                                                                                                             |
| CAMEO       | 1244                                                                                                                                                                                                                                                |
| Name        | Refuse to ease economic sanctions, boycott, or embargo                                                                                                                                                                                              |
| Description | Reject requests, refuse, or decline to reduce or eliminate economic sanctions, boycotts, or embargoes.                                                                                                                                              |
| Usage Notes | Use this code only for economic sanctions, boycotts, or embargoes.                                                                                                                                                                                  |
| Example     | US authorities said yesterday that removing the sanctions on Burma is currently out of the question as that would reward the regime for doing nothing.                                                                                              |
| CAMEO       | 1245                                                                                                                                                                                                                                                |
| Name        | Refuse to allow international involvement (non-mediation)                                                                                                                                                                                           |
| Description | Reject requests, refuse or decline to allow access to international actors such as observers, humanitarian agencies, and peacekeeping forces. Prospective peacekeepers, observers, etc. are coded as targets.                                       |
| Usage Notes | The UNITA militarist wing refused to allow United Nations planes to land and evacuate 15 of its observers who were taken hostage, the United Nations Observer Mission in Angola (MONUA) said.                                                       |
| Example     | Beirut again rejected Thursday a United Nations appeal for deploying army troops along its borders with Israel.                                                                                                                                     |
| CAMEO       | 1246                                                                                                                                                                                                                                                |
| Name        | Refuse to de-escalate military engagement                                                                                                                                                                                                           |
| Description | Reject requests, refuse, or decline to stop fighting or take measures to ease military conflict or tension.                                                                                                                                         |
| Usage Notes | Use this code for rejections of ceasefirees, military withdrawals, and demobilization.                                                                                                                                                              |
| Example     | Iran's religious leader Ayatollah Ruhollah Khomeini today rejected Iraqi President Saddam Hussein's proposal for a cease-fire during the Mosul holy month of Ramadan.                                                                               |
| Example     | Rebels in the Ivory Coast on Wednesday dismissed an appeal from President Laurent Gbago to lay down their arms, saying they had lost all trust in the government they rose up against on September 19.                                              |

| NAME        | 125                                                                                                                                                                                                                                                                                               | Reject proposal to meet, discuss, negotiate   |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| Description | Refuse to meet, discuss, or negotiate. Note that specific refusals to accept involvement of mediators or refusals to                                                                                                                                                                              |                                               |
| Usage Notes | meet with mediators are coded as 126 instead. Israeli President Moshe Katsav has refused to meet Jordan's visiting King Abdullah II in Tel Aviv, saying he would only welcome him in Jerusalem, his office said Tuesday. The radical Palestinian Islamic Jihad movement rejected an invitation to |                                               |
| Example     | attend a meeting next week of Palestinian factions to debate plans for inde- pendence from Israel, the group said Wednesday. Pakistan President Mohammad Zia-Ul-Haq today rejected a fresh offer from                                                                                             |                                               |
| Example     | Afganistan for direct talks between the two neighbors.                                                                                                                                                                                                                                            |                                               |
| NAME        | Refuse involvement of mediators or mediation initiatives. The target for this event should be the potential mediators.                                                                                                                                                                            |                                               |
| Usage Notes | Palestinian leader Yasser Arafat Wednesday rejected a US offer to host a summit in mid-July to hammer out a framework agreement for peace be- tween the Israelis and the Palestinians. Israel is opposed to French mediation in peace negotiations with Syria, a                                  |                                               |
| Example     | close aide to Prime Minister Ehud Barak said Wednesday.                                                                                                                                                                                                                                           |                                               |
| NAME        | Reject plan, agreement to settle dispute                                                                                                                                                                                                                                                          |                                               |
| Usage Notes | This event form refers typically, although not exclusively, to written and/or formal proposals of comprehensive settlements that seek to resolve a conflict. The target should be the opponent with whom the source is involved in a                                                              |                                               |
| Example     | Ivory Coast rebels on Friday again rejected a west African peace plan, and said they also opposed the deployment of a regional peacekeeping force until                                                                                                                                           |                                               |
| Example     | Newly appointed Palestinian Prime Minister Ismail Haniyeh has refused to respond to a demand from the US President to adhere to interim peace deals reached with Israel.                                                                                                                          |                                               |
| NAME        | Defy norms, law                                                                                                                                                                                                                                                                                   |                                               |
| Description | Disobey, challenge, or resist laws or norms.                                                                                                                                                                                                                                                      |                                               |
| Usage Notes | This event category covers both civilian disobedience and official defiance. The republic of Slovenia defied Yugoslav federal authority on Wednesday                                                                                                                                              |                                               |
| Example     | and was set to declare its right to secede from the country. A newspaper based in Christian east Beirut has violated a ban by General                                                                                                                                                             |                                               |
| Example     | Michel Aoun and described his rival Elias Hrawi as president.                                                                                                                                                                                                                                     |                                               |

| NAME        | 129                                                                                                                                                               |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Veto                                                                                                                                                              |
| Example     | Refuse to assent or formally reject legislative proposal, recommendation, or resolution. The United States on Wednesday vetoed a Security Council resolution cen- |
|             | ambassador's home in Panama on December 29.                                                                                                                       |

## 2.13 THREATEN

| NAME        | 130                                                                                                                                                                                                                                                                               |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Threaten, not specified below                                                                                                                                                                                                                                                     |
| Usage Notes | Threats are typically verbal acts. This residual category is not coded except when distinctions among codes 131-139 cannot be made. When any conflict-                                                                                                                            |
| Example     | President Reagan has threatened further action against the Soviet Union in an international television program beamed by satellite to more than 50 countries.                                                                                                                     |
| NAME        | Threaten non-force, not specified below                                                                                                                                                                                                                                           |
| Description | All non-force threats not otherwise specified.                                                                                                                                                                                                                                    |
| Usage Notes | This event form is a verbal act. It contains sub-forms for more detailed coding whenever possible. When non-force threats are actually carried out codes 160-166 should be used instead. Threats of administrative sanctions, such as bans or curfews, should be coded under 132. |
| Example     | Iran on Tuesday threatened to cut off electricity to the autonomous Azerbaijan republic of Nakhichevan over non-payment of bills, the official IRNA news agency reported.                                                                                                         |
| NAME        | Threaten to reduce or stop aid                                                                                                                                                                                                                                                    |
| Description | Threaten to reduce or stop providing material aid.                                                                                                                                                                                                                                |
| Usage Notes | Use this code for threats to reduce or eliminate provision of material assistance-economic, military, humanitarian, and peacekeeping.                                                                                                                                             |
| Example     | African states today announced that they will withdraw their peacekeeping force from Chad unless President Goukouni Oueddei arranged a ceasefire with rebels fighting to topple his government and held elections within four months.                                             |

| NAME        | Threaten to boycott, embargo, or sanction                                                                                                                                                                                                                                           |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Threaten to restrict normal economic interactions by imposing sanctions, boycotts, or embargoes.                                                                                                                                                                                    |
| Usage Notes | Use this code for the imposition of restrictions or restraints on economic exchange, typically on commerce and similar transactions as a way to protest or punish the target.                                                                                                       |
| Example     | A French minister threatened today to impose import restrictions against West German goods today as the leaders of the two countries sought to ease tensions in Franco-German relations.                                                                                            |
| NAME        | Threaten to reduce or break relations                                                                                                                                                                                                                                               |
| Description | Threaten to reduce or formally sever ties.                                                                                                                                                                                                                                          |
| Usage Notes | Non-force threats to declare independence, resign, withdraw diplomats, re-duce or break diplomatic ties, etc. are all coded here.                                                                                                                                                   |
| Example     | The Azerbaijani parliament threatened on Monday to secede from the Soviet Union unless the Kremlin withdrew its troops from the republic.                                                                                                                                           |
| Example     | Pakistan today threatened to break off diplomatic relations with Zaire and Costa Rica over their ties with Israel on the eve of a visit here by Palestine Liberation Organization (PLO) Chairman Yasser Arafat.                                                                     |
| Example     | Because of the compound target, two events are coded in this example. Palestinian leaders said they would boycott all official contact with the United States.                                                                                                                      |
| NAME        | Threaten with administrative sanctions, not specified below                                                                                                                                                                                                                         |
| Description | Threaten to impose or expand non-force administrative restrictions and penalties not otherwise specified.                                                                                                                                                                           |
| Usage Notes | Use sub-categories for more detailed coding whenever possible.                                                                                                                                                                                                                      |
| Example     | Greece, like most other existing members, plans to impose restrictions on its labour market for new EU members for at least two years from 1 May.                                                                                                                                   |
| NAME        | Threaten with restrictions on political freedoms                                                                                                                                                                                                                                    |
| Description | Threaten to impose or expand restrictions on fundamental freedoms, such as freedoms of speech, expression, and assembly.                                                                                                                                                            |
| Usage Notes | Note that if a threat indicates potential use of coercive repressive tactics as a way of enforcing the restrictions in question, 137 should be used instead. Israel threatened to ban voting in East Jerusalem if Hamas, which advocates Israel's destruction, ran in the election. |

| NAME        | Threaten to ban political parties or politicians                                                                                                                                                                                                                               |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Threaten to ban political activities of particular parties or individuals. If the target is being threatened with imprisonment or other measures of repression, 137 should be used instead.                                                                                    |
| Usage Notes | Israel's Cabinet met Sunday and decided to approve a plan that will not allow candidates from the militant group Hamas on the ballots there. President Yoweri Museveni has threatened to ban Ugandan opposition candidates from participating in the upcoming elections.       |
| CAMEO       | 1323                                                                                                                                                                                                                                                                           |
| Name        | Threaten to impose curfew                                                                                                                                                                                                                                                      |
| Description | Threaten to enforce a deadline beyond which inhabitants of an area are not permitted to be on the streets or in public places. President Laurent Gbagbo announced on Sunday that he will extend the night-time curfew in Algiers in response to recent unrest within the city. |
| Example     | Note that the future tense used in the lead implies a threat. President Abdelaziz Bouteflicka threatened to institute a curfew in Algiers in response to recent unrest within the city.                                                                                        |
| Example     | in response to recent unrest within the city.                                                                                                                                                                                                                                  |
| CAMEO       | 1324                                                                                                                                                                                                                                                                           |
| Name        | Threaten to impose state of emergency or martial law                                                                                                                                                                                                                           |
| Description | Threaten with suspending certain given rights or the whole constitution by imposing state of emergency or military rule.                                                                                                                                                       |
| Example     | Iraq's interim government announced that it is prepared to impose martial law as street battles raged in central Baghdad between insurgents and security forces.                                                                                                               |
| CAMEO       | 133                                                                                                                                                                                                                                                                            |
| Name        | Threaten to mobilize or engage in actions of political dissent such as protest demonstrations, hunger strikes, strikes or boycotts, physical obstructions into buildings or areas, and riots.                                                                                  |
| Example     | Radical French farmers said on Friday they would blockade Paris from Monday night to demand an end to the European Community's drastic farm reform.                                                                                                                            |
| Example     | Druze inhabitants of the Syrian Golan Heights threatened today to hold a general strike unless Israel rescinded its annexation of the region within 10 days.                                                                                                                   |

| NAME        | Threaten to halt negotiations                                                                                                                                                                                                                                                                              |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Threaten to break-up or withdraw from discussion, negotiation, or meeting.                                                                                                                                                                                                                                 |
| Usage Notes | Use this code for threats and warnings by source actors to stop negotiations, typically presented as protests against particular actions or policies of target actors.                                                                                                                                     |
| Example     | The Soviet Union has threatened to stop negotiations to reduce long-range nuclear weapons if the United States goes ahead with the planned deployment of new medium-range nuclear missiles in Europe, the Washington Post reported today.                                                                  |
| NAME        | Threaten to halt mediation                                                                                                                                                                                                                                                                                 |
| Usage Notes | Threaten to stop mediation activities. This event form is a verbal act. Use this event form to code threats and warnings by source actors-mediators or adversaries-to stop mediating or engaging in mediated talks.                                                                                        |
| Example     | The European Community may halt mediation efforts among Yugoslavia's feuding republics if cooperation by all parties founders, Dutch Foreign Minister Hans Van den Broek said on Tuesday.                                                                                                                  |
| NAME        | Threaten to halt international involvement (non-mediation)                                                                                                                                                                                                                                                 |
| Description | Threaten to reduce or stop international intervention by expelling or withdrawing observers, humanitarian agencies, peacekeepers, etc.                                                                                                                                                                     |
| Usage Notes | Threats by international agencies to withdraw their involvement as well as threats by host countries to expel such actors are coded here. Note that mediation related threats are coded as 135 instead.                                                                                                    |
| Example     | U.N. Secretary-General Kofi Annan announced on Monday that he will withdraw weapons inspectors and humanitarian workers from Iraq. Future tense in the lead indicates threat (i.e. it has not yet taken place).                                                                                            |
| NAME        | Threaten with repression                                                                                                                                                                                                                                                                                   |
| Description | Threaten dissidents with forcible subjugation.                                                                                                                                                                                                                                                             |
| Usage Notes | Threats to imprison as well as to use force to clamp down on opposition activities are coded here. Note that even though it might involve use of violence by police or other security forces, repression of dissidents is different from use of military force against another armed group; threats to use |
| Example     | Cairo's security chief has warned that police will no longer tolerate rallies by the Kifaya ("Enough") group.                                                                                                                                                                                              |

| NAME         | Threaten with military force, not specified below                                                                                                                                                                                                                                                    |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Threaten to use force not otherwise specified.                                                                                                                                                                                                                                                       |
| Usage Notes  | This event form is a verbal act and it contains sub-forms for more detailed coding whenever possible. More active expressions of threat to use force are coded under category 15.                                                                                                                    |
| Example      | Osama bin Laden's al-Qaeda terror network has threatened to deliver devast- tating blows to the United States and Israel, a Saudi-owned weekly reports. Because of the compound target, two events are coded.                                                                                        |
| Example Note | Because of the compound target, two events are coded.                                                                                                                                                                                                                                                |
| NAME         | Threaten blockade                                                                                                                                                                                                                                                                                    |
| Description  | Threaten to prevent entry into and/or exit from a territory using military measures.                                                                                                                                                                                                                 |
| Usage Notes  | This event form is typically a verbal act. NATO confirmed on Wednesday it would tighten the naval blockade of the rump Yugoslav state in the Adriatic with Albania's help.                                                                                                                           |
| Example      | 1382                                                                                                                                                                                                                                                                                                 |
| Name         | Threaten occupation                                                                                                                                                                                                                                                                                  |
| Description  | Threaten to occupy, seize control of the whole or part of a territory.                                                                                                                                                                                                                               |
| Usage Notes  | This event form is typically a verbal act and is distinct from 192, which refers to military occupations that have been or are being carried out. Ethnic Albanians have sworn to fight until they gain control of villages near Macedonia's border with Kosovo, Macedonian officials said Wednesday. |
| Example      | 1383                                                                                                                                                                                                                                                                                                 |
| Name         | Threaten unconventional attack                                                                                                                                                                                                                                                                       |
| Description  | Threaten to use unconventional violence, including terrorist activities. This event form is typically a verbal act and is distinct from unconventional attacks that are actually carried out (category 18).                                                                                          |
| Example      | The Hamas threatened Monday to resume terrorist activities in Israel in an escalation of the intifada (uprising).                                                                                                                                                                                    |
| NAME         | Threaten conventional attack                                                                                                                                                                                                                                                                         |
| Description  | Threaten to attack, use conventional weapons against a party. This event form is typically a verbal act.                                                                                                                                                                                             |
| Usage Notes  | Iran today threatened to launch a new military offensive in its Gulf war with Iraq unless Baghdad accepted its conditions for ending the 28-month- old conflict.                                                                                                                                     |
| Example      | Iran threatened to shell Iraqi towns today in retaliation for an air raid on the southern city of Susangerd where, it said, 100 people were killed.                                                                                                                                                  |

| NAME         | Threaten unconventional mass violence                                                                                                                                                                                                                                                                                                                                   |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Threaten to use force potentially affecting large masses of people, includ- ing the use of weapons of mass destruction (nuclear or chemical-biological- radiological attacks), mass expulsions or killings, as well as ethnic cleansing. This event form is typically a verbal act. Use this code for threats to carry out actions best represented in cue category 20. |
| Example      | A terror group based in Trinidad claims to be manufacturing chemical and biological weapons to use against the United States and Britain, according to a media report Sunday. Because of the compound target, two events are coded.                                                                                                                                     |
| EXAMPLE Note | Because of the compound target, two events are coded.                                                                                                                                                                                                                                                                                                                   |
| NAME         | Give ultimatum                                                                                                                                                                                                                                                                                                                                                          |
| Description  | Give a final warning, ultimate demand or order.                                                                                                                                                                                                                                                                                                                         |
| Usage Notes  | This event form is typically a verbal act. Use it to code final demands, rejec- tion of which carries the risk of some form of retaliation by the party issuing the ultimatum. Use of this code depends primarily on the terminology used by reporters-look for the word 'ultimatum', otherwise, it is simply a threat.                                                 |
| Example      | Peru has issued an ultimatum to Ecuador to halt attacks across their dis- puted jungle border.                                                                                                                                                                                                                                                                          |

## 2.14 PROTEST

| NAME        | Engage in political dissent, not specified below.                                                                                                                                                                                                                                                                                                                                                                                                   |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | All civilian demonstrations and other collective actions carried out as protests against the target actor not otherwise specified. This residual category is not coded except when distinctions among codes 141-145 cannot be made. Note that any form of civilian individual or collec- tive action that is undertaken as a symbol of support-rather than protest- for the target actor should be coded elsewhere (potentially under category 05). |
| Example     | The Homeland Union (Conservatives) began collecting signatures in part of a drive to convince the Lithuanian Parliament to amend the constitution so that same-sex marriages are banned.                                                                                                                                                                                                                                                            |

| Name        | Demonstrate or rally, not specified below                                                                                                                                                                                                                                                                                                                                                                                                                            |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Dissent collectively, publicly show negative feelings or opinions; rally, gather to protest a policy, action, or actor(s).                                                                                                                                                                                                                                                                                                                                           |
| Usage Notes | Use sub-categories if demands of protesters are known and codeable. The target for this event form is the party that the protest is directed against; the location of a demonstration sometimes represents the identity of the target. Up to 100 ethnic Albanians demonstrated on Tuesday in the Yugoslav province of Kosovo, where 24 people were killed in nationalist riots last March, Belgrade radio said.                                                      |
| Example     | March, Belgrade radio said.                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| CAMEO       | 1411                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Name        | Demonstrate or rally for leadership change                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Usage Notes | Dissent collectively, gather, or rally demanding leadership change. Target should be the actor who is expected to relinquish power. Demonstrations that demand new elections should also be coded here. Angry activists from the defeated Fatah Party have staged rallies in the Gaza Strip against the party's leader Mahmoud Abbas, saying he must resign.                                                                                                         |
| CAMEO       | 1412                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Name        | Demonstrate or rally for policy change                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Usage Notes | Dissent collectively, gather, or rally demanding policy change. Use this code when demonstrators demand specific policy changes or unspecified political reforms. Tens of thousands of university students throughout Indonesia staged mass demonstrations Saturday to demand political reforms by President Suharto's government.                                                                                                                                   |
| CAMEO       | 1413                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Name        | Demonstrate for rights                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Usage Notes | Dissent collectively, gather, or rally demanding political, social, economic, or other rights. Use this code for demonstrations that demand new rights or protest the violation of existing ones. Thousands of Nigerians from throughout the country were converging Thursday for a rally in Lagos to protest the rights violations under the recently imposed Sharia law by Islamic fundamentalists in the northern districts.                                      |
| CAMEO       | 1414                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Name        | Demonstrate for change in institutions, regime                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Usage Notes | Dissent collectively, gather, or rally demanding major institutional, constitutional, or regime change. Note the difference between institutional/constitutional changes and policy reforms. Demonstrations that call for independence or autonomy essentially demand major changes to the whole system and are hence coded here. Thousands of Iraqi Kurds demonstrated in the northern city of Kirkuk on Sunday calling for independence from Iraq, witnesses said. |

| CAMEO       | 142                                                                                                                                                                                                                                  |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | Conduct hunger strike, not specified below                                                                                                                                                                                           |
| Description | Protest by refusing to eat until certain demands are met, not further specified.                                                                                                                                                     |
| Usage Notes | Use sub-categories if demands of protesters are known and codeable. The target for this event form is the party against which the hunger strikers protest.                                                                           |
| Example     | Up to 1,000 ethnic Turks began a hunger strike on Monday to protest against Sweden's decision to send them back to Bulgaria, where they say they face imprisonment, homelessness and persecution.                                    |
| CAMEO       | 1421                                                                                                                                                                                                                                 |
| Name        | Conduct hunger strike for leadership change                                                                                                                                                                                          |
| Description | Refuse to eat until demands for leadership change are met.                                                                                                                                                                           |
| Usage Notes | Target should be the actor who is expected to relinquish power. Hunger strikes that demand new elections should also be coded here.                                                                                                  |
| Example     | Islamic fundamentalists continued their hunger strike to demand the resignation of Algerian President Ahmed Ben Bella.                                                                                                               |
| CAMEO       | 1422                                                                                                                                                                                                                                 |
| Name        | Conduct hunger strike for policy change                                                                                                                                                                                              |
| Description | Refuse to eat until demands for policy reform are met.                                                                                                                                                                               |
| Usage Notes | Use this code when protesters demand specific policy changes or unspecified political reforms.                                                                                                                                       |
| Example     | A member of the Syrian parliament, Mohammed Mamoun, started a hunger strike yesterday to protest President Assad's failure to usher in meaningful political reforms.                                                                 |
| CAMEO       | 1423                                                                                                                                                                                                                                 |
| Name        | Conduct hunger strike for rights                                                                                                                                                                                                     |
| Description | Refuse to eat until demands for political, social, economic, or other rights are met.                                                                                                                                                |
| Usage Notes | Use this code for hunger strikes that demand new rights or protest the violation of existing ones.                                                                                                                                   |
| Example     | Algerian landowners began a hunger strike outside Parliament to demand the return of property seized by Algerian government forces in the 1970s, APS news agency said.                                                               |
| Example     | Salaheddine Sidhoum, Algeria's leading human rights activist, staged a 24- hour hunger strike in prison on Sunday in protest against the widespread human rights violations by Algerian security forces, his lawyer said on Tuesday. |

| CAMEO       | 1424                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | Conduct hunger strike for change in institutions, regime                                                                                                                                                                                                                                                                                                                                                                              |
| Description | Refuse to eat until demands for major institutional, constitutional, or regime change.                                                                                                                                                                                                                                                                                                                                                |
| Usage Notes | Note the difference between institutional/constitutional changes and policy reforms. Hunger strikes that call for independence or autonomy essentially demand major changes to the whole system and are hence coded here. A group of Chenchen refugees are continuing a hunger strike in protest of the Russian government's refusal to accept the independence of Chechnya.                                                          |
| Example     | the Russian government's refusal to accept the independence of Chechnya.                                                                                                                                                                                                                                                                                                                                                              |
| Name        | Conduct strike or boycott, not specified below                                                                                                                                                                                                                                                                                                                                                                                        |
| Description | Protest by refusing to work or cooperate until certain demands are met, not specified further.                                                                                                                                                                                                                                                                                                                                        |
| Usage Notes | Use sub-categories if demands of protesters are known and codeable. The target for this event form is the party against which the hunger strikers protest. This event form does not refer to military strikes, which are coded under category 19 instead.                                                                                                                                                                             |
| Example     | Palestinians of the Israeli-occupied West Bank shunned work on Monday to protest at settlement of Soviet Jewish immigrants on Arab land.                                                                                                                                                                                                                                                                                              |
| Name        | Conduct strike or boycott for leadership change                                                                                                                                                                                                                                                                                                                                                                                       |
| Description | Refuse to work or cooperate until demands for leadership change are met. Target should be the actor who is expected to relinquish power. Strikes or boycotts that demand new elections should also be coded here. The fundamentalist Umma (Nation) party has said it will boycott Algeria's first multi-party elections unless the president agrees to step down. Ideally the Algerian president would have been coded as the target. |
| Example     | Conduct strike or boycott for policy change                                                                                                                                                                                                                                                                                                                                                                                           |
| Name        | Refuse to work or cooperate until demands for policy reform are met. Use this code when protesters demand specific policy changes or unspecified political reforms.                                                                                                                                                                                                                                                                   |
| Description | Use this code when protesters demand specific policy changes or unspecified political reforms.                                                                                                                                                                                                                                                                                                                                        |
| Example     | Some 500,000 workers affiliated with the Serbian Workers' Union (SSS) stopped work on the first day of an open-ended strike on Monday over a controversial employment bill signed in by Serbian Labour Minister Dragan Milovanovic.                                                                                                                                                                                                   |

| Name        | 1433                                                                                                                                                                                                                                                                                                                    |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Refuse to work or cooperate until demands for political, social, economic, or other rights are met.                                                                                                                                                                                                                     |
| Usage Notes | Use this code for strikes or boycotts that demand new rights or protest the violation of existing ones.                                                                                                                                                                                                                 |
| Example     | Seven opposition parties in Nepal have organized a general strike that shut down Khatmandu in protest of last week's arrest of a number of activists.                                                                                                                                                                   |
| CAMEO       | 1434                                                                                                                                                                                                                                                                                                                    |
| Name        | Conduct strike or boycott for change in institutions, regime                                                                                                                                                                                                                                                            |
| Description | Refuse to work or cooperate until demands for major institutional, constitutional, or regime change. Note the difference between institutional/constitutional changes and policy reforms. Strikes that call for independence or autonomy essentially demand major changes to the whole system and are hence coded here. |
| CAMEO       | 144                                                                                                                                                                                                                                                                                                                     |
| Name        | Obstruct passage, block, not specified below                                                                                                                                                                                                                                                                            |
| Description | Protest by blocking entry and/or exit into building or area, not otherwise specified.                                                                                                                                                                                                                                   |
| Usage Notes | Use sub-categories if demands of protesters are known and codeable. Use this event form to code protest activities that seek to disrupt routine and normal proceedings by blocking roads, buildings, etc. When the blockade in question includes military forces, use 191 instead.                                      |
| Example     | Angry French paper workers blocked the Europe Bridge spanning the Rhine from France to West Germany for more than three hours by dumping saw- dust on the roadway, French border police said.                                                                                                                           |
| CAMEO       | 1441                                                                                                                                                                                                                                                                                                                    |
| Name        | Obstruct passage to demand leadership change                                                                                                                                                                                                                                                                            |
| Description | Obstruct passage, block entry/exit to demand leadership change.                                                                                                                                                                                                                                                         |
| Usage Notes | Target should be the actor who is expected to relinquish power. Obstructions that demand new elections should also be coded here.                                                                                                                                                                                       |
| Example     | About 200 supporters of former President Ahmed Ben Bella blocked roads in the capital city of Algiers demanding that he be reinstated as leader of the Algerian government.                                                                                                                                             |
| Example     | Rebels in the Ivory Coast on Tuesday blocked transport into Abidjan as they continued their effort to overthrow the government of President Laurent Gbagbo.                                                                                                                                                             |

| Name        | 1442                                                                                                                                                                                                                                                                                                                                                  |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Obstruct passage, block entry/exit to demand policy reform.                                                                                                                                                                                                                                                                                           |
| Usage Notes | Use this code when protesters demand specific policy changes or unspecified political reforms. Demonstrators in Baghdad blocked a road to show their disapproval for the United States' military policies, a newspaper reported Tuesday.                                                                                                              |
| Example     | United States' military policies, a newspaper reported Tuesday.                                                                                                                                                                                                                                                                                       |
| Name        | 1443                                                                                                                                                                                                                                                                                                                                                  |
| Description | Obstruct passage to demand rights                                                                                                                                                                                                                                                                                                                     |
| Usage Notes | Use this code for obstructions that demand new rights or protest the violation of existing ones.                                                                                                                                                                                                                                                      |
| Example     | Young Algerians blocked roads leading to the city centre on Sunday to press their demands for greater freedom and opportunities from President Bouteflika's government.                                                                                                                                                                               |
| Name        | 1444                                                                                                                                                                                                                                                                                                                                                  |
| Description | Obstruct passage to demand change in institutions, regime                                                                                                                                                                                                                                                                                             |
| Usage Notes | Note the difference between institutional/constitutional changes and policy reforms. Obstructions that call for independence or autonomy essentially demand major changes to the whole system and are hence coded here. Hundreds of thousands of people blocked streets in Hong Kong in defiance of Chinese authorities to demand democratic reforms. |
| Example     | 145                                                                                                                                                                                                                                                                                                                                                   |
| Name        | Protest violently, riot, not specified below                                                                                                                                                                                                                                                                                                          |
| Description | Use sub-categories if demands of protesters are known and codeable. Use this event form to code demonstrations and protests that turn violent. When the use of force to cause casualties is the primary purpose, use categories 18, 19, or 20 instead.                                                                                                |
| Example     | Palestinian prisoners rioted Monday at this jail in northern Israel, setting fire to their mattresses and smashing furniture, police sources said.                                                                                                                                                                                                    |
| Name        | Engage in violent protest for leadership change                                                                                                                                                                                                                                                                                                       |
| Description | Protest forcefully, in a potentially destructive manner, to demand leadership change.                                                                                                                                                                                                                                                                 |
| Usage Notes | Target should be the actor who is expected to relinquish power. Riots that demand new elections should also be coded here.                                                                                                                                                                                                                            |
| Example     | Egyptian demonstrators rioted following a peaceful demonstration calling for the immediate removal of President Hosni Mubarak from office.                                                                                                                                                                                                            |

| NAME        | Engage in violent protest to demand policy change                                                                                                                                                                                                                                                                                                                                                  |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Protest forcefully, in a potentially destructive manner, to demand policy reform.                                                                                                                                                                                                                                                                                                                  |
| Usage Notes | Use this code when protesters demand specific policy changes or unspecified political reforms.                                                                                                                                                                                                                                                                                                     |
| Example     | Palestinian riots against Israeli military policies are still continuing with no end in sight.                                                                                                                                                                                                                                                                                                     |
| NAME        | Engage in violent protest to demand rights                                                                                                                                                                                                                                                                                                                                                         |
| Usage Notes | Use this code for riots that demand new rights or protest the violation of existing ones.                                                                                                                                                                                                                                                                                                          |
| Example     | Palestinian youths resorted to throwing stones during demonstrations against the alleged human rights violations by the Israeli military, officials said on Thursday.                                                                                                                                                                                                                              |
| NAME        | Engage in violent protest to demand change in institutions, regime                                                                                                                                                                                                                                                                                                                                 |
| Usage Notes | Protest forcefully, in a potentially destructive manner, to demand major institutional, constitutional, or regime change.                                                                                                                                                                                                                                                                          |
| Example     | Note the difference between institutional/constitutional changes and policy reforms. Riots that call for independence or autonomy essentially demand major changes to the whole system and are hence coded here. Prisoners rioted at a jail in East Timor's capital Dili on Monday joining thousands of demonstrators in demanding a referendum on independence from Indonesian rule, locals said. |

## 2.15 EXHIBIT MILITARY POSTURE

| NAME        | 150                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | All military or police moves that fall short of the actual use of force, not otherwise specified.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Usage Notes | This category is different from cue categories 18, 19, and 20, as they refer to uses of force, while military posturing falls short of actual use of force and is typically a demonstration of military capabilities and readiness. Category 15 is also distinct from category 13 in that the latter refers merely to threats, is typically verbal, and does not involve any activity that is undertaken to demonstrate military power. Note that source actors for codes 150-153 are not necessarily militaries affiliated with states but any organized armed groups. Targets are actors against whom the source mobilizes its military capabilities in a threatening manner. |
| Example     | The Macedonian army prepared to resume shelling Albanian rebel-held territory as attempts to resolve the crisis on the political front were deadlocked.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| NAME        | 151                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Description | Need new description.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Usage Notes | Need new usage notes.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Example     | NEED EXAMPLE.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| NAME        | Increase military alert status                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Description | Use this event form to code formal military orders to go on alert. The party against whom the military move is directed is the target actor.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Example     | Israeli troops remained on alert in the occupied West Bank today to forestall more violence after a week of unprecedented Palestinian civil unrest.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| NAME        | Mobilize or increase police power                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Description | Increase the number of military personnel and/or weapons.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Usage Notes | Use this code when the government mobilizes police power to demonstrate strength, mostly as a scare tactic.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Example     | The government of Sindh province has ordered patrols by police and paramilitary soldiers after violent protests by Muslim groups.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |

| NAME        | Mobilize or increase armed forces                                                                                                                                |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Increase the number of military personnel and/or weapons.                                                                                                        |
| Usage Notes | The party against whom the military move is directed is the target actor.                                                                                        |
| Example     | Israel has strengthened its forces in Lebanon following the discovery of Soviet-made Katyusha rockets in the area last week, military sources said today.        |
| Example     | Britain mobilized army reservists for a possible war against Iraq on Tuesday while UN arms inspectors said they needed more time.                                |
| NAME        | Mobilize or increase cyber-forces                                                                                                                                |
| Description | Increase the capacity to wage cyber-warfare.                                                                                                                     |
| Usage Notes | This event can only be coded when the move is directed against a specific target or targets, whether as an offensive or defensive move.                          |
| Example     | North Korea has trained more than 500 computer hackers capable of launching cyber warfare against the United States, South Korea's defense ministry said Monday. |

## 2.16 REDUCE RELATIONS

| NAME        | Reduce relations, not specified below                                                                                                                                                                                    |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | All reductions in normal, routine, or cooperative relations not otherwise specified.                                                                                                                                     |
| Usage Notes | This residual category is not coded except when distinctions among codes 161-166 cannot be made.                                                                                                                         |
| Example     | Italy announced a suspension of air links with Yugoslavia on Wednesday, one day after a Yugoslav army jet shot down a helicopter carrying EC truce monitors.                                                             |
| NAME        | Reduce or break diplomatic relations                                                                                                                                                                                     |
| Description | Curtail, decrease, break, or terminate diplomatic exchange.                                                                                                                                                              |
| Usage Notes | Cancellation of meetings, withdrawal, or expulsion of diplomats and termination of other diplomatic activities (excluding negotiations and mediations which are coded as 164 and 165 respectively) should be coded here. |
| Example     | A French minister has cancelled a planned visit to Haiti after a state of siege was declared in the one-time French colony, the Foreign Affairs Ministry said on Sunday.                                                 |
| Example     | Switzerland said today it had expelled two Soviet diplomats based in Geneva for spying, adding to a long series of espionage scares.                                                                                     |

| NAME        | Reduce or stop material aid, not specified below                                                                                                                                                                                                                                                                                                |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Reductions or terminations of aid not otherwise specified.                                                                                                                                                                                                                                                                                      |
| Usage Notes | This event form category contains sub-forms for more detailed coding whenever possible.                                                                                                                                                                                                                                                         |
| Example     | The United States announced Wednesday it would prohibit all aid to Albanian rebels in Macedonia and would deny entry to the United States to all individuals undermining stability there. Red Cross officials suspended aid deliveries in Baghdad on Wednesday after two of their vehicles were hit by gunfire and a staff member went missing. |
| CAMEO       | 1621                                                                                                                                                                                                                                                                                                                                            |
| Name        | Reduce or stop economic assistance                                                                                                                                                                                                                                                                                                              |
| Description | Decrease or terminate provision of economic aid.                                                                                                                                                                                                                                                                                                |
| Example     | Japan said on Tuesday it had halted economic aid to Yugoslavia in line with Western efforts to end the fighting there.                                                                                                                                                                                                                          |
| CAMEO       | 1622                                                                                                                                                                                                                                                                                                                                            |
| Name        | Reduce or stop military assistance                                                                                                                                                                                                                                                                                                              |
| Description | Decrease or terminate provision of military aid.                                                                                                                                                                                                                                                                                                |
| Example     | The United States suspended part of a military aid program for Bosnia aimed at bringing Bosnian Croat and Moslem armed forces together as a unified identity, the New York Times reported on Friday.                                                                                                                                            |
| CAMEO       | 1623                                                                                                                                                                                                                                                                                                                                            |
| Name        | Reduce or stop humanitarian assistance                                                                                                                                                                                                                                                                                                          |
| Description | Decrease or terminate provision of humanitarian aid.                                                                                                                                                                                                                                                                                            |
| Example     | The United Nations on Tuesday reduced food supplies to the biggest Cambodian refugee camp in Thailand because rice was being diverted to outside users, relief officials said.                                                                                                                                                                  |
| CAMEO       | 163                                                                                                                                                                                                                                                                                                                                             |
| Name        | Impose embargo, boycott, or sanctions                                                                                                                                                                                                                                                                                                           |
| Description | Stop or restrict commercial or other material exchange as a form of protest or punishment.                                                                                                                                                                                                                                                      |
| Example     | President Bill Clinton has imposed sanctions on the Taliban religious faction that controls Afghanistan for its support of suspected terrorist Osama bin Laden, the White House said Tuesday.                                                                                                                                                   |

| Name        | 164                                                                                                                                                                                                                                                                                                                                                                                                                    |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Halt negotiations                                                                                                                                                                                                                                                                                                                                                                                                      |
| Usage Notes | Use this event form to code failed negotiations and walk-outs, as well as other disruptions of planned negotiations. Note that the termination can be either unilateral or bi/multi-lateral.                                                                                                                                                                                                                           |
| Example     | Palestinians and Israelis failed to reach agreement on the fate of Palestinian offices in east Jerusalem Sunday, despite hours of tense negotiations, sources on both sides reported. Two reciprocal events are coded with actors reversed.                                                                                                                                                                            |
| CAMEO       | 165                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Name        | Halt mediation                                                                                                                                                                                                                                                                                                                                                                                                         |
| Usage Notes | The source for this event form is typically the mediating party(ies). Use this event form to code failed mediation activities.                                                                                                                                                                                                                                                                                         |
| Example     | Syrian officers today ended mediation efforts between rival militias in Tripoli as shells continued crashing into the north Lebanese port and the death toll rose to more than 200.                                                                                                                                                                                                                                    |
| CAMEO       | 166                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Name        | Expel or withdraw, not specified below                                                                                                                                                                                                                                                                                                                                                                                 |
| Description | Terminate the presence of groups or organizations not otherwise specified.                                                                                                                                                                                                                                                                                                                                             |
| Usage Notes | Use this category to code both expulsions by host authorities and withdrawals by guest groups or organizations. Note that expulsions or deportations of individuals-typically a legal matter-are coded as 174 instead. Mass expulsions of peoples are coded as 201. Withdrawal of hostile military forces constitutes a form of yielding and is thus coded as 0874. When diplomats are withdrawn or expelled, use 161. |
| CAMEO       | 1661                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Name        | Expel or withdraw peacekeepers                                                                                                                                                                                                                                                                                                                                                                                         |
| Description | Terminate the deployment or presence of peacekeeping forces.                                                                                                                                                                                                                                                                                                                                                           |
| Usage Notes | Use this event form to code both expulsions of peacekeeping forces by host countries and voluntary withdrawals by actors providing the peacekeeping forces. Note that while the host country should be coded as the source actor when coding an expulsion of peacekeeping forces, the provider of the forces becomes the source when coding withdrawals.                                                               |
| Example     | Eighty UN peacekeepers were shipped out of the eastern Bosnian enclave of Gorazde Friday, leaving just 100 UN troops to follow them out later this month.                                                                                                                                                                                                                                                              |

| NAME        | 1662                                                                                                                                                                                                                                     |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Expel or withdraw inspectors, observers                                                                                                                                                                                                  |
| Usage Notes | Use this event form to code both expulsions by host countries and withdrawals by providers of inspectors or observers.                                                                                                                   |
| Example     | North Korea expelled inspectors of the International Atomic Energy Agency, or IAEA, from frozen nuclear facilities at Yongbyon after U.S. officials alleged that the North admitted it had a uranium-based program in late 2002.         |
| CAMEO       | 1663                                                                                                                                                                                                                                     |
| Name        | Expel or withdraw aid agencies                                                                                                                                                                                                           |
| Description | Terminate the presence of aid agencies or other non-governmental organiza- tions helping civilians.                                                                                                                                      |
| Usage Notes | Use this event form to code both expulsions by host countries and withdrawals by providers of humanitarian aid. When aid is simply reduced or halted but the expulsion or withdrawal of the provider is not mentioned, use 1623 instead. |
| Example     | Jakarta forced the UN refugee agency, UNHCR, out of the country following the relief operation, although it had more than £12m of unspent donations.                                                                                     |

## 2.17 COERCE

| NAME        | Coerce, not specified below                                                                                                                                                       |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Repression, violence against civilians, or their rights or properties not oth- erwise specified.                                                                                  |
| Example     | Turkish police prevented the demonstration staged by students at Cumhuriyet University near AKP offices in Sivas on 15 October to protest the decision of sending troops to Iraq. |
| NAME        | Seize or damage property, not specified below                                                                                                                                     |
| Description | Use of force against property or violation of property rights not otherwise specified.                                                                                            |
| Usage Notes | This event form category contains sub-forms for more detailed coding when- ever possible.                                                                                         |
| Example     | Croatian authorities are failing to uphold the property rights of Croatian Serb refugees, a human rights group protested here Wednesday.                                          |

| Name        | 1711                                                                                                                                                                                                                                                                                                                                                                                      |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Use force to take control of somebody else's property, confiscate, expropriate.                                                                                                                                                                                                                                                                                                           |
| Usage Notes | Use this event form to code raids and lootings as well as other confiscations.                                                                                                                                                                                                                                                                                                            |
| Example     | In an unprecedented move, Palestinian police in Jericho confiscated weapons and explosives from Palestinian armed groups, the Israeli army said Friday.                                                                                                                                                                                                                                   |
| CAMEO       | 1712                                                                                                                                                                                                                                                                                                                                                                                      |
| Name        | Destroy property                                                                                                                                                                                                                                                                                                                                                                          |
| Description | Use force to destroy, demolish property.                                                                                                                                                                                                                                                                                                                                                  |
| Example     | Afghan guerillas blew up three main electric power lines leading into Kabul last month and nearly one third of the city's power supply is still down, the Czechoslovak news agency Ceteka reported from Kabul today.                                                                                                                                                                      |
| Example     | Jewish settlers in the West Bank city of Hebron set fire to the offices of the Palestinian administrators of Muslim property overnight following the killing of an Israeli man, Palestinian residents said Sunday. Israeli army bulldozers demolished Palestinian homes and civilian buildings in southern Gaza on Sunday, Palestinian officials and US witnesses said.                   |
| CAMEO       | 172                                                                                                                                                                                                                                                                                                                                                                                       |
| Name        | Impose administrative sanctions, not specified below                                                                                                                                                                                                                                                                                                                                      |
| Description | Formal decrees, laws, or policies aimed at curbing the rights of civilians not otherwise specified. This event form category contains sub-forms for more detailed coding when ever possible.                                                                                                                                                                                              |
| CAMEO       | 1721                                                                                                                                                                                                                                                                                                                                                                                      |
| Name        | Impose restrictions on political freedoms                                                                                                                                                                                                                                                                                                                                                 |
| Description | Violate or impose limitations on fundamental political rights such as freedoms of speech, expression, and assembly. Restrictions on media and activities of political dissent are coded here. Note that if the event is about the actual enforcement of such restrictions through repressive tactics, such as imprisonments and dispersion of demonstrations, 175 should be used instead. |
| Example     | The British government on Monday outlawed the largest Protestant extremist organization in Northern Ireland because of what it called its direct involvement in killing in the strife-torn province.                                                                                                                                                                                      |
| Example     | Nicaragua's Sandinista government today ordered the opposition newspaper La Prensa to suspend publication indefinitely, a spokesman for the paper said.                                                                                                                                                                                                                                   |
| CAMEO       | 1722                                                                                                                                                                                                                                                                                                                                                                                      |
| Name        | Ban political parties or politicians                                                                                                                                                                                                                                                                                                                                                      |
| Description | Prevent establishment or activities of political parties or politicians.                                                                                                                                                                                                                                                                                                                  |
| Example     | President Yoweri Museveni has banned Ugandan opposition candidates from participating in the upcoming elections.                                                                                                                                                                                                                                                                          |

| NAME        | 1723                                                                                                                                                                                                                                                                                                                                                                                                                               |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Impose curfew Set a deadline beyond which inhabitants of an area are not permitted to be on the streets or in public places.                                                                                                                                                                                                                                                                                                       |
| Example     | Turkish authorities have imposed a curfew in the town of Cizre in southeastern Turkey after a demonstration over fraud allegations in Sunday's local elections, security sources said here Tuesday.                                                                                                                                                                                                                                |
| CAMEO       | 1724 Impose state of emergency or martial law                                                                                                                                                                                                                                                                                                                                                                                      |
| Name        | Suspend normal constitutional rights and provisions by installing state of emergency or military rule.                                                                                                                                                                                                                                                                                                                             |
| Example     | The military government of President Prosper Avril declared a 30-day state of siege in Haiti on Saturday, suspending parts of the constitution and arresting political opponents, a spokeswoman for the U.S. embassy said.                                                                                                                                                                                                         |
| CAMEO       | 173                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Name        | Arrest, detain                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Usage Notes | Legal or extrajudicial arrests, detentions, or imprisonments. Use this code for both criminal and political detentions. Note, however, that taking of hostages is coded as 181 instead, and charges or lawsuits are coded as 115. Israeli soldiers arrested more than 100 Palestinians on Saturday in a security sweep of the Hebron area of the occupied West Bank, military sources said.                                        |
| CAMEO       | 174                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Name        | Expel or deport individuals                                                                                                                                                                                                                                                                                                                                                                                                        |
| Usage Notes | Formal removal or expulsion of individuals from territories, typically following legal proceedings. Expulsion of diplomats constitute reduction of diplomatic relations and should be coded as 'Reduce or break diplomatic relations' (161). Expulsion of peacekeepers, inspectors, or aid agencies refer to category 166. Mass political expulsions, with the purpose of ethnic cleansing for instance, are coded as 201 instead. |
| Example     | Ghanaian authorities have deported 168 Liberians for traveling without proper documents on a Swedish-registered vessel, a port official said Monday.                                                                                                                                                                                                                                                                               |
| CAMEO       | 175                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Name        | Use repression                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Description | Actively repress collective actions of dissent by forcing subjugation through crowd control tactics, arrests, etc.                                                                                                                                                                                                                                                                                                                 |
| Usage Notes | Note the difference between repression of dissidents and military engagements. Liberian riot police used tear gas to disperse demonstrators protesting election results in Monrovia.                                                                                                                                                                                                                                               |

| NAME        | 176                                                                                                                                                                                                                                |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Illegal or unauthorized attack on computers, networks, or accounts.                                                                                                                                                                |
| Usage Notes | Cyberattacks can be any of a wide range of acts, with an even wider range of motives. Vandalism of websites, theft of private electronic information, and the hostile shutting-down of networks all fit under this category.       |
| Example     | North Korea has tried to hack into the computers of South Korean army officers, officials said Tuesday.                                                                                                                            |
| Example     | Muslim hackers angered by the publication of cartoons of the Prophet Mohammed have defaced nearly 3,000 Danish Web sites over the past month in the biggest politically motivated cyber attack long-time observers have ever seen. |

## 2.18 ASSAULT

| NAME        | 180                                                                                                                                                                                                   |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Use of unconventional violence, not specified below                                                                                                                                                   |
| Usage Notes | Use this event form to code use of forms of force and violence that do not require high levels of organization or conventional weaponry, not otherwise specified.                                     |
| Example     | A temporary camp for Congolese refugees was attacked by Burundian militiamen armed with machetes, killing at least 156 people, the UN refugee agency reported.                                        |
| NAME        | Abduct, hijack, take hostage                                                                                                                                                                          |
| Description | Kidnap, take hostage, hijack, or forcibly seize control of an aircraft, car, bus, ship, etc.                                                                                                          |
| Example     | Afghan rebels have kidnapped up to 16 Soviet civilian advisers from a town bazaar and exploded a series of bombs in the capital Kabul, western diplomatic sources in neighboring Pakistan said today. |

| Name        | 182                                                                                                                                                                                                                                                                                                                                                                        |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Physically assault, not specified below                                                                                                                                                                                                                                                                                                                                    |
| Usage Notes | This event form category contains sub-forms for more detailed coding whenever possible. Beatings are coded here. Israeli soldiers routinely beat up Palestinian detainees on the occupied West Bank with the knowledge of senior officers, a court martial was told today.                                                                                                 |
| Example     | Bank with the knowledge of senior officers, a court martial was told today.                                                                                                                                                                                                                                                                                                |
| Name        | Sexually assault                                                                                                                                                                                                                                                                                                                                                           |
| Usage Notes | Use this event form to code rapes and other sexual assaults.                                                                                                                                                                                                                                                                                                               |
| Example     | U.S. border patrol agents sexually abused illegal Mexican immigrants with impunity, a human rights organization charged on Saturday.                                                                                                                                                                                                                                       |
| Name        | Torture                                                                                                                                                                                                                                                                                                                                                                    |
| Usage Notes | The distinction between 1822 and the default code 182 depend primarily on the particular terminology used by reporters. This code is used typically when "torture" is mentioned in the lead. Security forces in Guinea have tortured scores of Sierra Leonean and Liberian refugees, whom authorities blame for a border conflict, Human Rights Watch (HWR) said Thursday. |
| Name        | Kill by physical assault                                                                                                                                                                                                                                                                                                                                                   |
| Usage Notes | Killing individuals by physically assaulting them without the use of weaponry, through beating, torture, lynching, etc. When a physical assault-beating, torture, lynching, etc.-is specifically mentioned to have caused death, this code takes precedence over other codes for physical assault.                                                                         |
| Example     | A Palestinian prisoner died as a result of torture while in Israeli police custody, according to a report by a pathologist sent to Israel by Physicians for Human Rights.                                                                                                                                                                                                  |
| Name        | Conduct suicide, car, or other non-military bombing, not specified below                                                                                                                                                                                                                                                                                                   |
| Description | The use of explosive devices or improvised explosives outside of military engagements. This residual category is not coded except where distinctions among codes 1831-1834 cannot be made. Aerial bombings that involve the use of aircraft are coded as 195 instead.                                                                                                      |
| Example     | Irish nationalist guerrillas wounded two British soldiers in a bomb attack on Thursday, police said.                                                                                                                                                                                                                                                                       |

| NAME        | CAMEO                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 1831                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Carry out suicide bombing                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Carry out bomb attack with the intention of causing own death as well as other casualties.                                                                                                                                                                                                                                                                                                                                                                                                 |
| Usage Notes | Not every attack that results in the assailant's death is necessarily a suicide attack; we rely on the terminology used by reporters to make that call-we code bombings as suicide bombings if the report identifies it as such.                                                                                                                                                                                                                                                           | not every attack that results in the assailant's death is necessarily a suicide attack; we rely on the terminology used by reporters to make that call-we code bombings as suicide bombings if the report identifies it as such.                                                                                                                                                                                                                                                           |
| Example     | Two Palestinian suicide bombers killed 23 people as well as themselves late Sunday when they blew themselves up in Tel Aviv in the second-worst attack in the current Palestinian uprising, police said.                                                                                                                                                                                                                                                                                   | in the current Palestinian uprising, police said.                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Example     | At least three Iraqi civilians have been killed in a suicide car bombing in central Baghdad, Iraqi police said.                                                                                                                                                                                                                                                                                                                                                                            | at least three Iraqi civilians have been killed in a suicide car bombing in central Baghdad, Iraqi police said.                                                                                                                                                                                                                                                                                                                                                                            |
| CAMEO       | 1832                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Carry out vehicular bombing                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Name        | Carry out roadside bombing                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Carry out roadside bombing                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Usage Notes | These bombs or explosives are typically left along the roads by assailants long before they are detonated, hence reports of such attacks can rarely credibly identify the actors responsible for placing those explosives. Therefore, the particular locations of such attacks are typically coded as source actors.                                                                                                                                                                       | These bombs or explosives are typically left along the roads by assailants long before they are detonated, hence reports of such attacks can rarely credibly identify the actors responsible for placing those explosives. Therefore, the particular locations of such attacks are typically coded as source actors.                                                                                                                                                                       |
| Example     | A roadside bombing near the town of Samarra on Sunday killed one U.S. soldier and wounded two others, the military said.                                                                                                                                                                                                                                                                                                                                                                   | A roadside bombing near the town of Samarra on Sunday killed one U.S. soldier and wounded two others, the military said.                                                                                                                                                                                                                                                                                                                                                                   |
| CAMEO       | 1834                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Carry out location bombing                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Name        | The use of pre-placed explosive device(s) with the intent of causing casualties and or/structural damage.                                                                                                                                                                                                                                                                                                                                                                                  | The use of pre-placed explosive device(s) with the intent of causing casualties and or/structural damage.                                                                                                                                                                                                                                                                                                                                                                                  |
| Usage Notes | The distinguishing factors for this code are the presence of placed munitions detonated either remotely or according to pre-set conditions (time, proximity, movement of the device, etc.). Suicide, vehicular bombing components, or roadside locations take precedence and are coded 1831, 1832 and 1833 respectively. Minefield casualties and the deployment of mines are specifically excluded from this code and are coded as 193 (Fight with small arms and light weapons) instead. | The distinguishing factors for this code are the presence of placed munitions detonated either remotely or according to pre-set conditions (time, proximity, movement of the device, etc.). Suicide, vehicular bombing components, or roadside locations take precedence and are coded 1831, 1832 and 1833 respectively. Minefield casualties and the deployment of mines are specifically excluded from this code and are coded as 193 (Fight with small arms and light weapons) instead. |
| Example     | Three US servicemen were killed by an improvised explosive device outside of the Iraqi city of Basra.                                                                                                                                                                                                                                                                                                                                                                                      | of the Iraqi city of Basra.                                                                                                                                                                                                                                                                                                                                                                                                                                                                |

| Name                | Use as human shield                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description Example | Use civilians as buffer on the front lines or in other dangerous environments. The Sri Lankan army has been holding thousands of Tamil civilian refugees as human shields in the battle zones of the southern sector of the Jaffna peninsula, according to a press release by the Liberation Tigers.                                                                                                                                                                                                                                      |
| NAME                | Attempt to assassinate                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Usage Notes         | Attempt but fail to kill politically significant and influential persons. Use this code only when an assassination attempt or targeted killing is foiled; when assassinations are successfully carried out, 186 is used instead. This distinction is made because consequences of these two types of events could be significantly different. The source of this event would ideally be the assailant; however, in many cases this information will not be available and the location of the attack would be coded as the source instead. |
| Example             | An attempt to assassinate deputy governor of the Tyumen region, Oleg Chemezov, was thwarted in Khanty-Mansiysk (Siberia), the city's police reported.                                                                                                                                                                                                                                                                                                                                                                                     |
| Example             | Militants loyal to Iraq's Al-Qaeda frontman Abu Musab al-Zarqawi said they attempted to assassinate outgoing Prime Minister Iyad Allawi, in a statement posted on the internet.                                                                                                                                                                                                                                                                                                                                                           |
| NAME                | Assassinate                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Description         | Kill politically significant and influential persons.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Usage Notes         | Use this event form to code targeted killings and assassinations of politically influential elites or leaders.                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Example             | Hezbollah guerrillas killed the deputy chief of Israel's militia ally in southern Lebanon Sunday sources on both sides said. This example is coded as an assassination because of the position the victim held (which is explicitly reported).                                                                                                                                                                                                                                                                                            |

## 2.19 FIGHT

| NAME         | Use conventional military force, not specified below                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | All uses of conventional force and acts of war typically by organized armed groups not otherwise specified. This residual category is not coded except when distinctions among codes 191-196 cannot be made. In addition to unspecified acts of fighting, "killings" of any kind when the weapons used are not specified should also be coded here. When news leads refer to acts of killing that take place during an attack or some form of military engagement as "murders", those should still be coded here. However, murders in general-as criminal acts with no political connotations-are not coded under the CAMEO framework. The first example below illustrates how one can differentiate between these two different uses of the verb "murder". |
| Example      | One Serb policeman was murdered in an attack on a police patrol by Kosovo Albanians near the border with Kosovo, state agency Tanjug reported Sunday.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Example      | Vietnamese and Kampuchean forces were battling for control of a strategic base near the border today, Thai military sources said. Two reciprocal events are coded with actors reversed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Example      | Palestinian gunmen attacked an Israeli village close to the West Bank Sunday and killed an Israeli, public television reported.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| CAMEO        | Impose blockade, restrict movement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Name         | Impose blockade, restrict movement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Description  | Prevent entry into and/or exit from a territory using armed forces.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Usage Notes  | Note that this event form is different from code 144 ('Obstruct physically'), which refers to civilian protest activities that seek to disrupt routine and normal proceedings.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Example      | Israel Friday reimposed blockades in the West Bank following the shooting deaths of two Israelis a day earlier, a military spokesman announced. The Soviet Union closed its southern borders with Iran and Turkey because of fighting between Azerbaijanis and Armenians, an editor at the official                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Example Note | Due to the compound target, two events are coded.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |

| NAME         | Occupy territory                                                                                                                                                                                                                                                                                                                                     |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description  | Occup y seize control of a territo ry using armed forces.                                                                                                                                                                                                                                                                                            |
| Example      | Vietnamese-led forces have retak en a strategic village in Western Kampuchea after fierce fighting with guerrillas who overran it late last month, Thai military sources said today.                                                                                                                                                                 |
| Example      | Burmese troops have captured part of a Karen guerrilla stronghold on the Thai border after five days of fighting, Thai police here said on Monday. Israel today mounted its long-threatened invasion of South Lebanon, plough- ing through the United Nations lines on the coast of south of Tyre and thrusting forward in at least to inland areas. |
| CAMEO        | 193                                                                                                                                                                                                                                                                                                                                                  |
| Name         | Fight with small arms and light weapons                                                                                                                                                                                                                                                                                                              |
| Description  | Attack using small arms and light weapons such as rifles, machine-guns, and mortar shells. Small arms include revolvers and self-loading pistols, rifles and carbines, sub-machine guns, assault rifles and light machine-guns. Light weapons in-                                                                                                    |
| Usage Notes  | include heavy-machine guns, hand-held under-barrel and mounted grenade launchers, portable anti-aircraft guns, portable anti-tank guns, recoilless rifles, portable launchers of anti-tank missile and rocket systems, portable launchers of anti-aircraft missile system, and mortars of calib ers less than 100 mm.                                |
| Example      | Sudanese rebels shelled the southern regional capital Juba for the first time in a year on Sunday and Monday, killing about 20 people, relief officials in Nairobi said.                                                                                                                                                                             |
| Example      | Egyptian police opened fire to disperse Moslem fundamentalist demonstrators on Monday night, killing one person and arresting 12, security sources said.                                                                                                                                                                                             |
| Example      | Serb forces killed three ethnic Albanians in a gunbattle in southeastern Serbia Friday, a political council representing ethnic Albanians in the region said in remarks published here Sunday.                                                                                                                                                       |
| Example Note | Note that because the type of weapon used is specified, this code is used instead of the default code 190. A minefield explosion near the town of Samarra killed two Iraqi youths and wounded five others on Sunday.                                                                                                                                 |

| NAME        | Fight with artillery and tanks                                                                                                                                                                                                                                                                                                                                                                                                                           |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Attack using artillery, tanks, and rocket fire.                                                                                                                                                                                                                                                                                                                                                                                                          |
| Usage Notes | Use this event form to code military engagements that involve the use of guns of large caliber that are too heavy to carry, such as cannon or missile launchers that are not portable, and tanks and/or warships. When both small arms or light weapons and heavy weaponry are used, this code takes precedence.                                                                                                                                         |
| Example     | Vietnamese-led forces launched artillery, mortar, and rocket fire against Kampuchean guerrilla camps near the eastern Thai border today, killing or wounding 50, Thai military sources said. Israeli tanks fired four shell bombs at targets in Jericho, witnesses said, in a rare incident in the West Bank city.                                                                                                                                       |
| Example     | Imported aerial weapons, not specified below                                                                                                                                                                                                                                                                                                                                                                                                             |
| Name        | Employ aerial weapons, not specified below                                                                                                                                                                                                                                                                                                                                                                                                               |
| Description | Attack, bomb from air, not specified below.                                                                                                                                                                                                                                                                                                                                                                                                              |
| Usage Notes | Use this event form to code bombings that involve the use of military aircraft. When both aerial and other small types of weapons are used, this code takes precedence. This residual category is not coded except where distinctions among codes 1951-1952 cannot be made.                                                                                                                                                                              |
| Example     | Soviet aircraft including helicopter gunships killed 46 Afghan civilians in an attack on a village in the western province of Heart. Israeli helicopters and tanks shelled positions of the Palestinian security forces and residential areas near the town of Rafah.                                                                                                                                                                                    |
| Name        | Employ precision-guided aerial munitions                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Description | The use of aerial weapons that utilize internal and/or remote sensing and guidance controls to strike specific targets. The distinction between 1951 and the default 195 depends on whether the particular terminology used by reporters is indicative of guided or precision weapons. The weapons themselves must have guidance capability and should be differentiated from "surgical aerial attacks" which are otherwise coded under the default 195. |
| Example     | British aircraft using precision guided missiles killed 4 Iraqis in an attack on a suspected weapons supply in Basra.                                                                                                                                                                                                                                                                                                                                    |

| NAME        | 1952                                                                                                                                                                                                                                                                       |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | The use of remotely piloted or unmanned aerial platforms for the delivery or ordinance.                                                                                                                                                                                    |
| Usage Notes | Use this event form to code aerial attacks that involve the use of unmanned or remotely piloted vehicles. This code takes precedence over the use of precision guided munitions (1951).                                                                                    |
| Example     | Recent US Predator attacks, occurring about once every three days, have killed at least eight top al-Qaeda leaders since last July, according to Pentagon sources.                                                                                                         |
| NAME        | Violate ceasefire                                                                                                                                                                                                                                                          |
| Usage Notes | Reinitiate fighting in the midst of a formal or informal ceasefire or truce.                                                                                                                                                                                               |
| Example     | Both the Phillippines military and the Moro Islamic Liberation Front are guilty of violating the ceasefire agreement signed in March 2001, according to a group that conducted simultaneous fact-finding missions in Lanao, Maguindanao, and Cotabato provinces last week. |
| NAME        | Two reciprocal events of the same type are coded.                                                                                                                                                                                                                          |

## 2.20 ENGAGE IN UNCONVENTIONAL MASS VIOLENCE

| NAME        | Use massive unconventional force, not specified below                                                                                                                                                                                                                                              |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | All uses of unconventional force that are meant to cause mass destruction, casualties, and suffering not otherwise specified. This residual category is not coded except when distinctions among codes 201-204 cannot be made.                                                                     |
| NAME        | Engage in mass expulsion                                                                                                                                                                                                                                                                           |
| Description | Force large groups of people or populations out of some territory.                                                                                                                                                                                                                                 |
| Usage Notes | Note that this event form is different from expulsions of diplomats and international or non-governmental groups (166), and legal deportations (174). Mass expulsions coded here are typically carried out with the intention of clearing out a particular group of people out of a specific area. |
| Example     | The Israeli army forced out on Wednesday more than 1,000 Palestinian refugees from their homes in a West Bank refugee camp during a 48-hour search for militants, residents said.                                                                                                                  |

| NAME        | Engage in mass killings                                                                                                                                                                                                                                                                                                                                                                     |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Description | Kill a substantial number of people, typically with the intention of ridding a territory of a particular group of people.                                                                                                                                                                                                                                                                   |
| Usage Notes | Politically motivated mass killings and genocides are coded here, relying primarily on the specific terminology used by reporters to identify an event that involves "mass" killings.                                                                                                                                                                                                       |
| Example     | Sudan's government is responsible for mass killings and other atrocities in the Darfur region, according to a United Nations report.                                                                                                                                                                                                                                                        |
| NAME        | Engage in ethnic cleansing                                                                                                                                                                                                                                                                                                                                                                  |
| Description | Use mass expulsions and/or mass killings targeting a specific ethnic group.                                                                                                                                                                                                                                                                                                                 |
| Usage Notes | When a report identifies mass expulsions or mass killings as being motivated by ethnic cleansing, use this code instead. The only way we can code ethnic cleansings as such is only if reporters use that particular terminology; therefore, we will need to rely on careful analysis of our event data, whereby we would focus on particular dyads, to reliably measure ethnic cleansings. |
| Example     | Serb forces were engaged in ethnic cleansing in Kosovo against the majority Albanian population of the province, according to the US government.                                                                                                                                                                                                                                            |
| NAME        | Use weapons of mass destruction, not specified below                                                                                                                                                                                                                                                                                                                                        |
| Description | Attack with unconventional weapons that are meant to cause massive destruction and casualties.                                                                                                                                                                                                                                                                                              |
| NAME        | Use chemical, biological, or radiological weapons                                                                                                                                                                                                                                                                                                                                           |
| Description | Attack using chemical, biological, or radiological weapons.                                                                                                                                                                                                                                                                                                                                 |
| NAME        | Detonate nuclear weapons                                                                                                                                                                                                                                                                                                                                                                    |
| Description | Attack using nuclear weapons.                                                                                                                                                                                                                                                                                                                                                               |

## Chapter 3

## ACTOR CODEBOOK

Actor and agent dictionaries are developed to systematically assign codes to names (of individuals, countries, identity groups, organizations, etc.) that refer to source or target actors in news reports. Several regional dictionaries have been developed within the framework of the CAMEO project. In addition to laying out the format and the rules that apply commonly to the creation of new codes in actor and agent dictionaries, this codebook documents the shared and region-specific actors that existed in the dictionaries at the time of this codebooks compilation (as well as some updates from subsequent revisions). It does not contain an exhaustive list of all agent and actor codes utilized in the various KEDS/CASCADE projects that make use of the CAMEO coding schemes. Coders who modify CAMEO or add new codes (not names, but general types) should record the changes made.

As projects have demanded more specificity from CAMEO codes, the complexity and length of CAMEO codes have increased. Early CAMEO codes may be simpler than strict adherence to the rules below would imply.

## 3.1 HIERARCHICAL RULES OF CODING
Actor codes are composed of a series of three-letter groups, written in the order pictured above. The length of the code given to any actor depends on the number of these groups applicable to an actor and necessary for the needs of the coding group, but TABARI currently limits the total number of characters to fifteen, i.e. five three-letter codes. Some actors may be deemed important enough to warrant a three character code unique to themselves, but most just use a combination of specific and generic codes.

Coding of any actor follows two basic rules:

- 1. Proceed from the general to the specific.
- 2. Maintain a consistent pattern (ideally the one above) in choosing the hierarchical placement of appropriate three letter classifications.

No actor will use all the categories listed, but rules and hierarchy provide the coder with a clearer path of how an actor's coding scheme should break down and ensures some level of consistency

across studies.

## 3.1.1 Domestic or International?

There are two types of actor in the CAMEO coding scheme: domestic and international. How an actor is coded depends on which of those types the actor is.

For a domestic actor, the first three characters of the CAMEO code indicate the actor's country. The United Nations list of standard three-letter country codes is used to identify countries. The current list, as well as a list of changed and added codes, can be found at the UN website (http://unstats.un.org/unsd/methods/m49/m49.htm). A list of UN country codes is also presented in Chater ?? .

Actors that cannot readily accept a single national identifier may instead take an international code. Different generic codes are used to differentiate between various kinds of international and transnational actors. IGO (international governmental organization), IMG (international militarized group), NGO (non-governmental organization), NGM (non-governmental movement), and MNC (multinational corporation) are the main generic codes. They can either be used on their own or as the first three characters of more detailed codes. A few special cases-religious groups, ethnicities, and international regions-are handled as international actors but do not begin with international codes.

In addition, we have the code UIS (unidentified state actor), which is used when an actor is known to be a country or government-or it is known to act on behalf of a country or state-but the identity of the particular country is not revealed in the report (e.g. "foreign diplomat"). Similarly, if an international actor cannot be categorized for whatever reason, INT can be used as the last-resort, catch-all code. UIS and INT are typically used as three-letter codes on their own.

The following subsections describe how a domestic actor is coded, in order from left to right in the code. The differences for international codes are described in subsection 3.1.9.

## 3.1.2 Domestic Region

In countries with federal systems, autonomous regions, other forms of decentralization, or any other idiosyncratic facts that render regional distinctions politically significant, our codes link actors to sub-state regions as well as countries. Assigning actors domestic region codes (as the second three characters) allows researchers to code and study intrastate events which might have domestic as well as international significance. Sub-state codes are often essential components of a regional dictionary-the Balkans is one such case. Serbia during 2003-2006, for example, is assigned the code [SCGSRB] , where SCG is the UN code for the state of Serbia and Montenegro and SRB denotes the Republic of Serbia, which was a sub-state entity within Serbia and Montenegro.

In some cases, we have assigned geographic regions within a country their own three character codes because the distinction was important for demographic or other political reasons, even though these regions did not have legal status. For Turkey, we have given Southeast Turkey its own code ( [TURSOE] ), which has allowed us to capture many domestic events (particularly between Kurdish insurgents and the Turkish state) that we otherwise could not. A comprehensive list of all sub-state region codes can be found in the respective region-specific sections of this codebook.

## 3.1.3 Primary Role Code

Generic role codes are assigned to actors in order to indicate their roles and statuses, when known and relevant, within their respective countries. They are appended to the initial country and

regional codes.

A comprehensive list of generic role codes can be found in Table 3.1. We make a crucial distinction between primary, secondary, and tertiary role codes. Coders should use primary codes to identify the role of a domestic actor wherever reasonable; among those, GOV , MIL , OPP , and INS or SEP (formerly REB ) are in fact the most commonly used.

REB has been, for most of CAMEO's history, the catch-all term for violent opposition groups. SEP and INS were added in late 2009, and they have more or less replaced that code for specific actors. However, REB still is used to code cases where a violent opposition group's aims are unclear, or where the group has very plainly limited goals (i.e. not involving separating from overthrowing the government). Also, older projects using CAMEO use only the REB code, and, depending on the project, coders may choose not to use SEP or INS . Coders should be sure, however, to distinguish between these kinds of actors and those assigned a secondary role code of CRM (see subsection 3.1.6). While CRM actors may utilize violent operations, they primarily exist for the purpose of achieving monetary profit or other self-gratification and not for the achievement of political aims through violent efforts.

UAF should be used as a last resort when an armed group cannot be identified either as MIL or REB . This situation tends to arise when the association of a given armed group with the state it operates in is unclear (e.g. whether it is an independent rebel group or a paramilitary), or the group is accepted but not controlled by the state. If the link between a paramilitary and a state is common knowledge, however, MIL should still be used-even though the group might not officially be part of the state military institution. The Serb Volunteer Guard, also known as Arkan's Tigers, for instance, should be coded as [SRBMIL] .

Note that actor codes with domestic roles will often need date restrictions to reflect changing roles of actors through the span of the dataset. This is especially true when coding countries that experience frequent power changes. Section 3.2.1 details how such restrictions are added.

Table 3.1: Generic Domestic Role Codes

| Primary Role Codes   | Description                                                                                                                                                             |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| COP                  | Police forces, officers, criminal investigative units, protective agencies                                                                                              |
| GOV                  | Government: the executive, governing parties, coalitions partners, executive divisions                                                                                  |
| INS                  | Insurgents (rebels): all rebels who attempt to overthrow their national government                                                                                      |
| JUD                  | Judiciary: judges, courts                                                                                                                                               |
| MIL                  | Military: troops, soldiers, all state-military personnel/equipment                                                                                                      |
| OPP                  | Political opposition: opposition parties, individuals, anti-government activists                                                                                        |
| REB                  | Rebels: armed and violent opposition groups, individuals                                                                                                                |
| SEP                  | Separatist rebels: all rebels who try to emancipate their region from its country                                                                                       |
| SPY                  | State intelligence services and members including covert operations groups as well as intelligence collection and analyses                                              |
| UAF                  | Armed forces aligned neither with nor against their government                                                                                                          |
| Secondary Role Codes | Description                                                                                                                                                             |
| AGR                  | Agriculture: individuals and groups involved in the practices of crop cultivation including government agencies whose primary concern is agricultural issues            |
| BUS                  | Business: businessmen, companies, and enterprises, not including MNCs                                                                                                   |
| CRM                  | Criminal: corresponding to individuals involved in or allegedly involved in the deliberate breaking of state or international laws primarily for profit                 |
| CVL                  | Civilian individuals or groups sometimes used as catch-all for individuals or groups for whom no other role category is appropriate                                     |
| DEV                  | Development: individuals or groups concerned primarily with development issues of varying types including infrastructure creation, democratization et al.               |
| EDU                  | Education: educators, schools, students, or organizations dealing with education                                                                                        |
| ELI                  | Elites: former government officials, celebrities, spokespersons for organizations without further role categorization (George Soros, former Secretary of Defense, Bono) |
| ENV                  | Environmental: entities for whom environmental and ecological issues are their primary focus, includes wildlife preservation, climate change, etc.                      |
| HLH                  | Health: individuals, groups and organizations dealing with health and social welfare practices (doctors, Doctors Without Borders)                                       |
| HRI                  | Human Rights: actors for whom their primary area of operation or expertise is with documenting and/or correcting human rights concerns                                  |
| LAB                  | Labor: specifically individuals in or elements of organized labor, organizations concerned with labor issues                                                            |
| LEG                  | Legislature: parliaments, assemblies, lawmakers, references to specific legislative entities or sub-entities such as committees                                         |
| MED                  | Media: journalists, newspapers, television stations also includes providers of internet services and other forms of mass information dissemination                      |
| REF                  | Refugees: also refers to agencies or MNCs dealing with population migration and relocation issues                                                                       |
| Tertiary Role Codes  | Description                                                                                                                                                             |
| MOD                  | Moderate: "moderate," "mainstream," etc.                                                                                                                                |
| RAD                  | Radical: "radical," "extremist," "fundamentalist," etc.                                                                                                                 |

## 3.1.4 Party or Speciality (Primary Role Code)

The PTY (party) distinction is a special role code that comes after primary role codes but before anything else. Political organizations receive the designation PTY when they field candidates for local or national elections, they are considered legal/legitimate by the current political regime, and they are not, at an organizational level, armed or violent. Individuals receive the designation PTY if they are members of qualified political organizations but are not members of the national or local executive. The PTY designation, whenever possible, comes immediately after OPP or GOV . Whether a party is in opposition or government depends solely on whether it is a member of the executive at the highest level of government for which it fields candidates.

Alternatively, a second primary role code can be appended to the first to represent an actor's area of power or concern. This happens, for example, with secretaries and ministers of defence; though they are part of the government, they exercise control over military affairs and are thus coded [XXXGOVMIL] . This case is discussed in more detail in section 3.2.5.

## 3.1.5 Ethnicity and Religion

In the latest version of the system, we have a detailed, global classification system for both religious and ethnic groups: these are discussed in Chapters 10.0.4 and ?? . These have not, however, been systematically incorporated into all of the dictionaries.

## 3.1.6 Secondary Role Code (and/or Territory)

If none of the primary codes applies to the actor in question, coders should choose from secondary role codes. Hence, for instance, a labor union would have the LAB code and a given journalist would have the MED code only if they cannot be identified as OPP . However, this restriction does not preclude the addition of secondary role codes to the primary code if such distinctions would be valuable to the coders. An opposition labor union, for example, would code as XXXOPPLAB .

Although we have a code for the legislative branch ( LEG ), it is identified as a secondary code and used sparingly. When a given legislative body is mentioned as an organization (e.g. the parliament, the House of Commons, the Senate), LEG is always used. When a particular political party or individual member of the legislature is in question, however, the convention has been to use GOVPTY or OPPPTY , depending on whether the relevant party has control of the executive branch . If the coders are more interested in the differentiation between the executive and legislative branches of a government or if control of the executive is separate from control of the legislature it may be more useful to code these actors as LEG .

Outside of religious applications, tertiary role codes should be used only as last resort. RAD captures ambiguous identifiers such as "radical," "extremist," and "fundamentalist" which can be encountered in news reports but do not refer to any systematically identifiable group or role. We felt compelled to create the code to systematize the the coding of such ambiguous labels, the meaning of which could vary from reporter to reporter and across regions: Does the term "extremist" refer simply to the conservative nature of a group or does it imply that the group in question is armed and violent? In order to avoid bias and to ensure reliability, RAD (and not REB ) should be used in such cases. For example, "extremist Serbian nationalist" should be coded as [SERRAD] . Similarly, MOD should be used when ambiguous identifiers such as "moderate" and "mainstream" are encountered.

## 3.1.7 Specialty (Secondary Role Code)

Secondary role codes can also be included in a CAMEO code to indicate an actor's specialty (much like in subsection 3.1.4. They can be added not only to primary role codes, but also to ethnicities, religions, or even other secondary role codes. For example, a legislative committee concerned with education would be coded as [ XXXLEGEDU] , while a Muslim student dissident would be [ XXXOPPMOSEDU] .

Tertiary role codes are used in this position as additional modifiers to facilitate the grouping of specific types of actors if one's analysis requires such a distinction, for example applying the designation of RAD to specific actors associated with known fringe or extremist groups. However, use of these codes should be driven by necessity, either because of the specificity required for the analysis or because of limitations in the source texts.

## 3.1.8 Organization Code

In cases where the coder wants to and can-given the amount of information available in the news lead-distinguish between different actors of the same generic domestic role, different groups can each be given their own three-character codes, which are then be used as the last three-characters. For example, the Likud and Meretz Parties in Israel are assigned the nine character codes of [ ISRGOVLKD] or [ ISROPPLKD] and [ ISRGOVMRZ] or [ ISROPPMRZ] , respectively. 1

Organization codes, especially for IGOs and NGOs, restart the cycle of role codes. Hence, a subunit of the specially coded actor may receive a code for its specialty. For example, the High Commission for Refugees is a suborganization within the United Nations, which has a special actor code (IGOUNO). The High Commission's code is simply added onto the U.N.'s code, becoming IGOUNOREFHCR: " REF " for refugee, " HCR " as its own special actor code.

## 3.1.9 International Codes

International codes apply to all actors who identify with more than one state. Most international actors' codes begin with a generic international code.

Table 3.2 defines the major international codes, along with examples. Notice that some of these examples are simply assigned the three character generic codes, while others are further specified with both generic and specific codes.

The distinction between NGO and NGM is meant to capture the theoretical difference between well-structured, formal non-governmental organizations and anomic or non-associational social movements. Although the line dividing the two is often fuzzy, we believe that the distinction is theoretically important-perhaps more so for some research questions than others. Greenpeace, for instance, is one of those difficult cases: although it is typically thought to be an NGO, it actually functions more as a loose and informal movement with some more formal organizations, such as the Greenpeace Foundation and Greenpeace USA, associated with it.

The IMG code is intended to identify those non-governmental groups, organizations, and movements on the international or regional level for whom militarized operations are their primary means of interacting within the international system. The distinction between an IMG and a domestic rebel group can be subtle. We define a militarized group to be international only if both its goals and its activities are substantially international.

$^{1}$Note that both of these codes need to be date-restricted appropriately since their roles as ‘government’ versus ‘opposition’ change regularly. Also, the project using these codes predated the introduction of the PTY code; were they coded now, they would be [ ISRGOVPTYLKD] , [ ISROPPTYLKD] , and so-on.

Sometimes news articles refer to unnamed actors such as "human rights advocates," "antiWTO protesters," and "supporters of Palestine". Such actors are best coded as NGM since they clearly belong to some non-governmental collective effort but, at the same time, are not explicitly associated with specific organizations. "Aid workers," on the other hand, are coded as NGOs, since participation in aid distribution generally requires an organization-even if the identity of the group is not specified in the news lead.

Some international actors do not always need a generic international codenamely, transnational regions, ethnicities, and religions. Moreover, the ordering and use of codes is slightly different for international actors than for domestic actors. We list these differences below.

Table 3.2: International/Transnational Generic Codes

| Generic Code   | Actor Type                                                                                          | Example                                                          | Full Code               |
|----------------|-----------------------------------------------------------------------------------------------------|------------------------------------------------------------------|-------------------------|
| IGO            | International or regional Inter-governmental organization                                           | "the United Nations" "World Trade Organization"                  | IGOUNO IGOWTO           |
| IMG            | International or regional International Militarized Groups                                          | "al-Qaeda" "Abu Sayaaf"                                          | IMGOSALQ IMGSEAMOSASF   |
| INT            | International or transnational actors who cannot be further specified as IGO, UIS, NGO, NGM, or MNC | "international envoy" "international observer" "world community" | INT INT INT             |
| MNC            | Multi-national corporations                                                                         | "Halliburton" "multinational firm" "Shell oil company"           | MNC MNC MNC             |
| NGM            | Non-governmental movements                                                                          | "Greenpeace" "anti-WTO activists" "human rights advocate"        | NGMENVGRP NGM NGM       |
| NGO            | Non-governmental organizations                                                                      | "aid worker" "Amnesty International" "Red Cross"                 | NGO NGOHRIAMN NGOHLHIRC |
| UIS            | Unidentified state actors                                                                           | "foreign diplomat" "world governments"                           | UIS UIS                 |

Location Sometimes news reports do not specify a group of countries separately and instead refer to them using the general geographical region they are associated with, such as Latin America ( LAM ), the Middle East ( MEA ), Eastern Europe ( EEU ), etc. In such cases, where exact identification of the countries involved is not possible, international region codes laid out in Table 3.3 can be used as the first three characters, which then typically constitutes the entire code.

In some cases, actors are primarily transnational/international in nature, yet their country affiliations are also known. Coders can include both pieces of information by attaching country codes to the generic transnational/international codes. This could be particularly valuable if, given the research agenda, the country distinction becomes key at the analysis stage. (For example, actors with codes NGOUSA , NGMUSA , and MNCUSA can all be combined with other USA actors at that stage, while still preserving the full codes/information in the dictionaries for alternative groupings.) (See sections 2D and 2E.) Attaching the country code does not indicate that the actor is officially identified with or that he acts on behalf of that state. The same technique can be used when only a regional affiliation is known-NATO's code, for example, includes " WST " to indicate that it is a Western organization.

Table 3.3: International Region Codes

| Region          | Code   |
|-----------------|--------|
| Africa          | AFR    |
| Asia            | ASA    |
| Balkans         | BLK    |
| Caribbean       | CRB    |
| Caucasus        | CAU    |
| Central Africa  | CFR    |
| Central Asia    | CAS    |
| Central Europe  | CEU    |
| East Indies     | EIN    |
| Eastern Africa  | EAF    |
| Eastern Europe  | EEU    |
| Europe          | EUR    |
| Latin America   | LAM    |
| Middle East     | MEA    |
| Mediterranean   | MDT    |
| North Africa    | NAF    |
| North America   | NMR    |
| Persian Gulf    | PGS    |
| Scandinavia     | SCN    |
| South America   | SAM    |
| South Asia      | SAS    |
| Southeast Asia  | SEA    |
| Southern Africa | SAF    |
| West Africa     | WAF    |
| "the West"      | WST    |

Ethnic and Religious Codes Some ethnic or religious identity groups are not strictly associated with single countries, thereby requiring their own three character codes. These codes are assigned as the first three character codes when not explicitly linked to a specific location or country. Even groups connected to a country may not be domestic actors. Albanians are significant not only in the state of Albania but in other Balkan countries as well; therefore, when news reports specifically mention ethnic Albanians and not the state of Albania, we distinguish between the two by assigning the code ABN as opposed to ALB, which corresponds to Albania.

However, some international organizations have distinct ethnic or religious identities-especially IMG's-in which case, an identity code can be used in conjunction with a generic international code and any number of other codes. Hence, Al Qaeda is coded as [IMGMOSALQ] .

Role Code (Any) International organizations can be coded to show their composition, purpose, or area of expertise. For instance, a multinational media corporation would code as [MNCMED] , with perhaps the interjection of the country where it is headquartered. Coders may use more than one role code, if they feel they must-only be sure to maintain the order of primary before secondary before tertiary.

Organization Code Some international/transnational actors get their own special three charac -ter codes (e.g. UNO for the United Nations, AMN for Amnesty International, IRC for the Red Cross), but these are used only as suffixes to these generic actor codes and any other specifying codes (i.e. [IGOUNO] , [NGOHRIAMN] , [NGOHLHIRC] ). Table 3.4 lists such actors who are currently assigned their own special codes in our regional dictionaries; both regionally and globally relevant actors are listed, but note that this list need not be final and coders/researchers can give other actors their own codes.

As an exception, we also have a six-character generic code used for peacekeeping forces when the particular organizational affiliation is not known: IGOPKO . This code is assigned even when the national identity of the peacekeepers in question is specified. Hence, for instance, "Senegalese peacekeepers" are coded as IGOPKO since they operate as part of an inter-governmental organization and they might be representing the United Nations or ECOWAS.

Second Specialty and Suborganization Code Often, an important IGO or NGO, worthy of its own organization code, is actually part of another important actor (usually the United Nations). When this situation arises, the overarching organization is coded first, and the specialty of the suborganization (if there is one) is added on the end, followed by its specific code. For example, the High Commission for Refugees is a suborganization within the United Nations, which has a special actor code (IGOUNO). The High Commission's code is simply added onto the U.N.'s code, becoming IGOUNOREFHCR: " REF " for refugee, " HCR " as its own special actor code. Be sure to avoid accidentally breaking the "primary before secondary" rule-the suborganization's specialty cannot be a primary role code if the organization's specialty is a secondary role code.

Third Specialty A third specialty code can occasionally be used when the spokesperson for an organization is identified (coded MED ).

Table 3.4: International/Transnational Actors with Special Codes

|              | International/Transnational Actors                      | Code   |
|--------------|---------------------------------------------------------|--------|
| Africa       | African Development Bank                                | IGOAFB |
|              | Arab Bank for Economic Development in Africa            | IGOABD |
|              | Bank of Central African States (BEAC)                   | IGOBCA |
|              | Common Market for Eastern and Southern Africa           | IGOCEM |
|              | Community of Sahel-Saharan States (CENSAD)              | IGOCSS |
|              | Eastern and Southern African Trade and Development Bank | IGOATD |
|              | Economic and Monetary Union of West Africa (UEMOA)      | IGOUEM |
|              | Economic Community of Central African States            | IGOECA |
|              | Economic Community of West African States (ECOWAS)      | IGOWAS |
|              | Franc Zone Financial Community of Africa                | IGOCFA |
|              | Inter-African Coffee Organization (IACO)                | IGOIAC |
|              | Intergovernmental Authority on Development (IGAD)       | IGOIAD |
|              | Monetary and Economic Community of Central Africa       | IGOCEM |
|              | New Economic Partnership for Africa's Development       | IGONEP |
|              | Organization of African Unity (OAU)                     | IGOOAU |
|              | Pan-African Parliament                                  | IGOPAP |
|              | Southern African Development Community                  | IGOSAD |
|              | West Africa Development Bank                            | IGOWAD |
|              | West Africa Monetary and Economic Union                 | IGOWAM |
| Middle East  | Arab Cooperation Council                                | IGOACC |
|              | Arab Economic Unity Council                             | IGOAEU |
|              | Arab League                                             | IGOARL |
|              | Arab Maghreb Union                                      | IGOAMU |
|              | Arab Monetary Fund for Economic and Social Development  | IGOAMF |
|              | Gulf Cooperation Council                                | IGOGCC |
|              | Org. of Arab Petroleum Exporting Countries (OAPEC)      | IGOAPE |
| Asia, Europe | Asian Development Bank                                  | IGOADB |
|              | Association of Southeast Asian Nations (ASEAN)          | IGOASN |
|              | Commonwealth of Independent States                      | IGOCIS |
|              | Council of Europe                                       | IGOCOE |
|              | Council of Security and Cooperation in Europe (OSCE)    | IGOSCE |
|              | European Bank for Reconstruction and Development        | IGOEBR |
|              | European Free Trade Association                         | IGOEFT |
|              | European Union                                          | IGOEEC |
|              | South Asian Association                                 | IGOSAA |
|              | Southeast Asia Collective Defense Treaty (SEATO)        | IGOSOT |
| Global       | Amnesty International                                   | NGOAMN |
|              | Association of Coffee Producing Countries               | IGOCPC |
|              | Bank for International Settlements                      | IGOBIS |
|              | Cocoa Producer's Alliance                               | IGOCPA |
|              | Commonwealth of Nations                                 | IGOCWN |
|              | Group of Eight (G-8) (G-7 plus Russia)                  | IGOGOE |
|              | Group of Seven (G-7)                                    | IGOGOS |
|              | Group of Seventy-Seven (G-77)                           | IGOGSS |

| International/Transnational Actors                      | Code      |
|---------------------------------------------------------|-----------|
| Highly Indebted Poor Countries (HIPC)                   | IGOHIP    |
| Human Rights Watch                                      | NGOHRW    |
| International Atomic Energy Agency (IAEA)               | IGOUNOIAE |
| International Cocoa Organization (ICCO)                 | IGOICO    |
| International Commission of Jurists                     | NGOJUR    |
| International Court of Justice (ICJ)                    | IGOUNOICJ |
| International Criminal Court                            | IGOICC    |
| International Crisis Group                              | NGOICG    |
| International Federation of Human Rights (FIDH)         | INGOFID   |
| International Fed. of Red Cross and Red Crescent (ICRC) | NGOCRC    |
| International Grains Council                            | IGOIGC    |
| International Helsinki Federation for Human Rights      | NGOIHF    |
| International Labor Organization                        | IGOUNOILO |
| International Monetary Fund (IMF)                       | IGOIMF    |
| International Organization for Migration                | NGOIMOM   |
| International War Crimes Tribunals                      | IGOUNOWCT |
| Inter-Parliamentary Union                               | IGOIPU    |
| Interpol                                                | IGOITP    |
| Islamic Development Bank                                | IGOIDB    |
| Medecins Sans Frontieres (Doctors Without Borders)      | NGOMSF    |
| North Atlantic Treaty Organization (NATO)               | IGNONAT   |
| Organization of American States                         | IGOOAS    |
| Organization of Islamic Conferences (OIC)               | IGOOIC    |
| Organization of Non-Aligned Countries                   | IGNONON   |
| Organization of Petroleum Exporting Countries (OPEC)    | IGOOPC    |
| Oxfam                                                   | NGOXFM    |
| Paris Club                                              | IGOPRC    |
| Red Cross                                               | NGOIRC    |
| Red Crescent                                            | NGORCR    |
| United Nations                                          | IGOUNO    |
| United Nations Children's Fund (UNICEF)                 | IGOUNOKID |
| United Nations Food and Agriculture Organization        | IGOUNOFAO |
| UN High Commission for Human Rights                     | IGOUNOHCH |
| UN High Commission for Refugees                         | IGOUNOHCR |
| World Bank                                              | IGOUNOWBK |
| World Economic Forum                                    | NGOWEF    |
| World Food Program                                      | IGOUNOWFP |
| World Health Organization                               | IGOUNOWHO |
| World Trade Organization (WTO)                          | IGOWTO    |

## 3.2 OTHER RULES AND FORMATS

## 3.2.1 Date R estrictions

Many actor codes require date-restrictions to limit the period for which TABARI will assign that code to the actor. The format of these codes do not deviate from the framework laid out below except for the inclusion of specific dates, which indicate the periods that correspond to each of the different codes. The need for date restrictions arise when the dataset covers a long period and the roles of individuals/groups/organizations-even the names and structures of states-change during this span.

Political power frequently changes hands in Israel. Hence, we cannot give the Israeli Labor Party, for example, a single code that specifies its domestic role. Instead, we code it as daterestricted, capturing when the party was part of the administration and when it played the role of opposition. 2

ISRAELI LABOR PARTY [ISROGLV LBA

This entry indicates that the Labor Party acted as part of the Israeli government for all of the specified periods and as the opposition during all other times. Furthermore, due to its prominent role in Israeli politics, the party is given its special three-character code ( LBA ), which sets it apart from other opposition groups or coalition partners in case the researcher wishes to make that distinction at the analysis stage.

Even states sometimes need to be date-restricted when previously sovereign states (or parts of other states) merge (e.g., East and West Germany, North and South Yemen, and North and South Vietnam) or existing states breakup to create multiple new ones (e.g. Yugoslavia, Czechoslovakia, and Ethiopia/Eritrea). For instance, Serbia has the code

SERBIA [YUGSRB

which indicates that Serbia was part of the Socialist Federal Republic of Yugoslavia up until it gained its independence in 1992, after which it formed the Federal Republic of Yugoslavia (with Montenegro), which became the new state-a looser federation-of Serbia and Montenegro after February, 2003. On 5 June 2006, the union of Serbia and Montenegro was dissolved and they each became separate sovereign states.

For a more comprehensive explanation of date-restrictions, readers should refer to Chapter 5 of the TABARI manual (available at http://eventdata.psu.edu/software.dir/tabari.html).

## 3.2.2 Actors and Agents

TABARI makes use of two different types of dictionary in order to appropriately code sources and targets of event data. Actor dictionaries came first, containing singular pattern-matchable entries with specific actor codes. Each actor had to be given its own entry into the appropriate actor dictionary. In early 2009, this process was augmented by the creation and addition of agent dictionaries. Rather than list specific actors explicitly, the agent dictionaries use commonly recurring words to categorize actors and help alleviate the need for redundancy in the actor dictionaries. For example, the word "admiral" indicates that an actor should be classified MIL . Once ADMIRAL is added to the agents dictionary, TABARI will automatically add the code MIL to the end of the actor's code in

$^{2}$Recall that the project in which Israel was coded preceded the addition of the PTY code.

the output file when admiral is found near the actor's name. (This is subject to being overridden by specific entries in the actor dictionaries. For example, the entry ADMIRAL NELSON would be read before the agent, allowing him to be identified as a historical figure, rather than a military actor.)

Actor entries take precedence over agent entries, as the actor codings are presumed to be more specific. Where the agent and actor codings would result in duplication of classifications, the duplicate is ignored. Therefore, if ANTRIM is in the actor dictionary coding as [USAMIL] and ADMIRAL is in the agent dictionary (coding as [~MIL] ), then TABARI on seeing the actor "Admiral Antrim" will code the resulting as [USAMIL] and not [USAMILMIL] . TABARI does not combine agent codings. Hence, for example, while both " STUDENT " (coding as [~EDU] ) and " DISSIDENT " (coding as [~OPP] ) may be present in agent dictionaries, TABARI will not read "student dissident" as [~EDUOPP] . Instead, STUDENT DISSIDENT must be explicitly entered into the agent dictionary. This was done to avoid situations in which "student dissident" and "dissident student" would code differently ( EDUOPP and OPPEDU respectively). Implementation of a hierarchical system for combining multiple agents into a single actor coding may be part of future implementations of TABARI as a further effort to cut down on the need for seemingly redundant dictionary entries.

## 3.2.3 Dictionaries

Currently the agent dictionaries are comprised of separate dictionaries for the GOV , MIL , OPP , and REB codes as well as a generic agent dictionary that handles references for secondary and tertiary role codes. As indicated previously there are also two agent dictionaries for the correct capture of religious codings (differentiated by their level of specificity). Additional helpful dictionaries to the coder are the NGO actor, the Elite actor, and the IMG dictionaries.

The elite actor dictionary has entries for a number of prominent organizations or individuals that would code with the ELI designation. Unfortunately most of the entries are specific to the US making it of limited value to those coding other regions. The IMG dictionary is a work in progress capturing actors that would be associated with several groups that fall under the IMG classification. In some cases only the name of the organization and known other appellations are listed but for some prominent members or leaders are also listed and provided with appropriate codes. For example "Osama bin Laden" is captured by this dictionary and assigned the appropriate IMG MOSALQ coding.

The NGO actor dictionary covers a wide variety of NGOs that a coder might want to capture. Rather than assign specific three character codes for every NGO/IGO efforts have been made to capture these actors with the appropriate International/Transnational actor code followed by a state or geographic region code (indicating either home country of the actor or primary region of its activities) and role codes (usually secondary) that indicate its primary area of expertise. Ethnic or religious identifications have also been captured where they were deemed appropriate.

## 3.2.4 Automatically-coded Celebrities

TABARI will code elites automatically in certain sentences. One will note that within the secondary role codes the code ELI specifically mentions former government officials. This is implemented within TABARI by recognizing that the word "former" as part of an agent or actor coding will cause the recognized pattern to be discarded in favor of the ELI secondary role code. Hence, "former Federal Reserve Chairman Alan Greenspan" will code as USAELI instead of USAGOV . Should TABARI fail at deleting double-codes, a Grep filter of the results can do the same task.

## 3.2.5 Coding Conventions

A number of examples have already been provided in the above sections but it seems worthwhile to point out a few additional as well as examples of coding conventions that can be utilized so as to standardize actor coding across coders.

One such convention is used to distinguish between various members of the US Department of Defense. Most actors in the Defense Department should be coded with the designation MIL followed by either SPY (if connected to military intelligence) or GOV if they are service specific or below (the Commandant of the Marine Corp or Secretary of the Navy for instance). All DoD personnel above this level that are responsible for policy setting code as GOVMIL as they are primarily associated with the government but their role within the government is military oriented.

## Chapter 4

## CAMEO Religious Coding Scheme

## 4.1 Introduction

CAMEORCS provides a greater level of detail for coding religion than the shorter CAMEO format by systematically assigning alphanumeric codes to individual religious groups and generalized religious terms. It was created during the summer of 2010 as a part of a larger, CAMEO-based project, and is thus intended as an optional supplement to CAMEO codes. The longer codes are used in actor codes in the exact same place and manner as the simple religious codes. Further, at every level of coding, CAMEORCS grandfathers in the religious codes used by CAMEO's shorter format.

The CAMEORCS directory includes a relatively comprehensive list of religious groups. However, projects may require adding more-and more specific-codes. Adding and coding new religious groups follows the same two rules from actor coding and adds two more.

- GLYPH Proceed from the general to the specific.
- GLYPH Maintain the hierarchical ordering prescribed by the manual.
- GLYPH As far as it is possible, code religious groups by their defining and distinguishing characteristics.
- GLYPH The manual describes which codes to prioritize; follow its prioritization.

CAMEORCS is restricted to three spaces (i.e. nine letters), so coders must be picky about which codes they use.

## 4.1.1 Self-Identification

CAMEORCS is not intended to be a grand theological treatise on who's who in the spiritual world. Coding must balance how a group regards itself and how it is regarded by others-especially its coreligionists. In the same vein, this scheme gives groups religious codes whenever plausible. Many organizations today have been called religious but do not regard themselves in this way. These groups nonetheless receive religious codes. Codeable groups include any organizations, communities, and fraternities based around a common philosophy, faith, or ethic. However, do not code religious groups that are dead during the time period of study.

## 4.1.2 Individualism

Each religious group, down to the lowest plausible level, is given its own distinct code. In addition, some relevant generic terms, e.g. "conservative Anglican", receive their own codes. However, the coder must choose the level of detail to which he or she codes-coding individual congregations would not be plausible. Consistency is not needed; for example, the original directory includes individual Catholic monastic orders, but only denominations (or even associations of national denominations) within Protestantism. In short, include everything worth coding.

## 4.1.3 Hierarchies

Often, groups would apparently take different code than the category above them. For example, non-trinitarian Christians are generally coded as CHRMAY , but a few trinitarian congregations nonetheless have constituent groups that are not. In this type of case, coherency may overrule accuracy; when a subgroup is accepted by its group, code it with that group.

## 4.2 First trio of letters

The first three letters of a religious code identify a specific religion or family of religions. Every religion that claims five million adherents or more receives its own code, as designated by prior coding (see Table 4.1.) Offshoots of a religion are given the code of their parent religion, unless they themselves have an individual code (e.g. Christianity, Sikhism, etc.)

Smaller religions are not given their own three-letter codes. Instead, they are categorized within families of religions. We use the common division annotated in the list below. A given religion may have strong influences from more than one of these families, in which case the coder must choose the best fit. Of the families of religions, new religious movements ( NRM ) hold a special place. They describe religious or philosophical movements, communities and companies created in the last century-and-a-half. The NRM code has lowest priority. For example, the code for a new Indian religious movement would begin with INR , not NRM .

Table 4.1: Religious Codes: First Three Letters

|                 | Group/Religion              | Code   |
|-----------------|-----------------------------|--------|
| First Priority: | Atheism/Agnosticism         | ATH    |
| Named           | Bahai Faith                 | BAH    |
| Religions       | Buddhism                    | BUD    |
|                 | Christianity                | CHR    |
|                 | Confucianism                | CON    |
|                 | Hinduism                    | HIN    |
|                 | Jainism                     | JAN    |
|                 | Judaism                     | JEW    |
|                 | Islam                       | MOS    |
|                 | Shintoism                   | SHN    |
|                 | Sikhism                     | SIK    |
|                 | Taoism                      | TAO    |
| Second          | Abrahamic religions         | ABR    |
| Priority:       | African diasporic religions | ADR    |
| Religious       | East Asian religions        | EAR    |
| Families        | Indian religions            | INR    |
|                 | Iranic religions            | IRR    |
|                 | Indigenous tribal religions | ITR    |
| Third Priority  | new religious movements     | NRM    |

## 4.3 Second trio of letters

The second trio of letters divides the first category further.

## 4.3.1 Denominations

First, if the first trio is a a named religion, the second trio can indicate a significant denomination or movement of that religion, e.g. Protestantism from Christianity, Shiism from Islam, or Zen from Buddhism. A complete collection of these codes can be found in the CAMEORCS directory.

## 4.3.2 Generic terms

Alternatively, the second trio can be a generic religious code. Such codes, listed in Table 4.2, simply serve to divide the first groupings into more manageable chunks, and generally apply across religions and family groups. These generic codes are ranked in priority in the table.

MAY , OFF , and NRM serve special roles within named religions, and we define them closely to handle delicate religious issues. MAY is used when a religious group considers itself a part of the parent religion, but the parent religious at least in large part rejects its inclusion. OFF applies to religious groups who do not consider themselves a part of the religion from which they are derived. (Whether the parent religion agrees is disregarded.) New religious movements ( NRM ) refer to movements that are widely regarded as being within the religion but outside any named sudivision, and were created in roughly the last century-and-a-half. Within religious families, NRMs have the same meaning as they would if used as the first three letters (see Section 4.2).

## 4.3.3 Generic, or Denominational?

Since CAMEORCS is designed to code actors, generic terms can sometimes override named denominations. Unitarian-Universalism, for example, comes from the Protestant tradition but does not self-identify as Christian-hence, it is only sensible to code it as CHROFF . The same phenomenon can occur with any generic codes that might describe heterodoxy, but it always occurs with OFF .

## 4.3.4 Region

For all indigenous tribal religions ( ITR ), the second set of letters should be a transnational region, taken from the listings in [the CAMEO actors manual]. Hence, indigenous tribal religions are organized by their geographic origins. This system will inevitably result in the occasional odd code, like [USAITSEA##] ( USA for United States and SEA for Southeast Asia), thanks to immigration.

## 4.3.5 Nothing

Finally, when there are no applicable specific or generic codes, the second trio can simply be left blank. Ecumenical organizations will usually skip secondary codes, as will general groupings like "conservative [religion]".

Table 4.2: Religious Codes: Second Three Letters

|                 | Group/Religion              | Code   |
|-----------------|-----------------------------|--------|
| First Priority  | offshoot                    | OFF    |
| Second Priority | named denominations         |        |
| Third Priority: | African diasporic religions | ADR    |
| Specific Items  | gnostic                     | GNO    |
|                 | millenarian                 | MLN    |
|                 | pagan                       | PAG    |
|                 | racialist                   | RAC    |
|                 | syncretic                   | SYN    |
|                 | extraterrificial            | UFO    |
|                 | wellness-centric            | WLN    |
| Fourth Priority | controversial status        | MAY    |
| Fifth Priority  | new religious movements     | NRM    |

## 4.4 Third trio of characters

[CAMEORC] codes are completed by a number between 001 and 999. Once again, some codes will skip this trio, namely general categories ("Protestant" as opposed to "Lutheran"). The earliest numbers in a set (001-009 or 001-099) are reserved for generic terms, e.g. "conservative" or "evangelical" or "moderate", etc. The header of categories can describe both the group described and the mainstream of that group. For example, [CHRLDS000] refers to both any unknown group or person within the Latter Day Saints movement and the Church of Jesus Christ of Latter-Day Saints (e.g. mainstream Mormons, as opposed to splinter groups.)

After the generic terms, the numerical codes can be manipulated to form subcategories. For

example, we divide Judaism in the tens column: Liberal Judaism is [JEW050] , Neolog Judaism is [JEW060] , Orthodox Judaism is [JEW070] , and so-on. Subsets of Liberal Judaism would be [JEW051] , [JEW052] , [JEW053] , etc. New Japanese Religions (which come from Shinto) are divided in the hundreds column, into Sect Shinto [SHNNRM100-200] and Shinshukyo [SHNNRM300-400] . Sect Shinto is then subdivided in the tens column, because it has relatively few subgroups, whereas Shinshukyo is divided in the singles column.

Initially, the religious directory has been arranged in alphabetical order (within subsets). However, when adding to the directory, add to the end of whatever category is desired. Creating an alphabetized directory of codes is a matter of a few minutes in Excel, whereas reconciling earlier work to a newly-numbered version of the coding scheme is much trickier. Thus, do not change the order of entries.

Giving an organization its own numerical code ameliorates the effect of coding mistakes and subjectivity. To use a silly hypothetical, suppose the dictionary writer were to mistakenly code Scientology as a form of Orthodox Christianity. In practice, so long as the codes are not combined in the analytical level, Scientology will be [CHRDOX###] (remember, this is a hypothetical!) and generic Orthodoxy will be [CHRDOX000] -so the two can be distinguished, and someone looking at the behaviour of the actors will see that the two are distinct (and potentially catch the miscode.) When in doubt, add a number!

## 4.5 Religion-specific coding issues

Religions tend to be as comparable as apples and oranges. As such, different religions are divided slightly differently, we list the major differences below.

## 4.5.1 Christianity

A coder must exercise considerable restraint in adding religious groups to the directory of Christianity - as a both institutionally fractious and very large religion, the number of identifiable Christian groups and denominations vastly outnumber the spaces available for coding. The MAY code sees extensive use in Christianity. We place groups in this category if they follow a non-trinitarian doctrine, worship their leaders, or add new scriptures to the Biblical canon.

## 4.5.2 Hinduism

Hinduism is rarely treated by scholars as a single religion, but instead as a group of related religions. Simultaneously, it may be plausibly divided by two methods: by denomination/deity or by philosophy. Hence, instead of denominations, Hinduism's named subcategories are purely taxonomical: HINAST for its Astika ("orthodox") schools, and HINDEN for its denominations. The hundreds place within these sectarian indicate which denomination or school is coded. Most Hindu organizations will be alphabetized within their denomination or philosophy, rather than placed under another level of hierarchy-the requisite information for coding often is absent.

## 4.5.3 Judaism

Judaism can best be divided into its movements. However, we also provide a section for the quasie ethnic distinctions of Ashkenazi, Sephardic, etc. The former categorization always takes priority.

## 4.5.4 Shintoism

Shintoism was especially profoundly affected by the worldwide religious shift that started in the mid-nineteenth century, with hundreds of new religious movements being birthed since then. The standing of these organizations in regard to Shinto is not always well-defined. Rather than dividing these "Japanese new religions" into NRM , MAY , and OFF , we categorize them all as "NRM".

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

## Chapter 6

## CAMEO EVENT CODES

## 01: MAKE PUBLIC STATEMENT

010: Make statement, not specified below

011: Decline comment

012: Make pessimistic comment

013: Make optimistic comment

014: Consider policy option

015: Acknowledge or claim responsibility

016: Deny responsibility

017: Engage in symbolic act

018: Make empathetic comment

019: Express accord

## 02: APPEAL

020: Make an appeal or request, not specified below

021: Appeal for material cooperation, not specified below

0211: Appeal for economic cooperation

0212: Appeal for military cooperation

0213: Appeal for judicial cooperation

0214: Appeal for intelligence

022: Appeal for diplomatic cooperation (such as policy support)

023: Appeal for aid, not specified below

0231: Appeal for economic aid

0232: Appeal for military aid

0233: Appeal for humanitarian aid

0234: Appeal for military protection or peacekeeping

024: Appeal for political reform, not specified below

0241: Appeal for change in leadership

0242: Appeal for policy change

0243: Appeal for rights

0244: Appeal for change in institutions, regime

025: Appeal to yield, not specified below

0251: Appeal for easing of administrative sanctions

0252: Appeal for easing of political dissent

- 0253: Appeal for release of persons or property
- 0254: Appeal for easing of economic sanctions, boycott, or embargo
- 0255: Appeal for target to allow international involvement (non-mediation)
- 0256: Appeal for de-escalation of military engagement
- 026: Appeal to others to meet or negotiate
- 027: Appeal to others to settle dispute
- 028: Appeal to engage in or accept mediation

## 03: EXPRESS INTENT TO COOPERATE

030: Express intent to cooperate, not specified below

031: Express intent to engage in material cooperation, not specified below

0311: Express intent to cooperate economically

0312: Express intent to cooperate militarily

0313: Express intent to cooperate on judicial matters

0314: Express intent to cooperate on intelligence

032: Express intent to engage in diplomatic cooperation (such as policy support)

033: Express intent to provide material aid, not specified below

0331: Express intent to provide economic aid

0332: Express intent to provide military aid

0333: Express intent to provide humanitarian aid

0334: Express intent to provide military protection or peacekeeping

034: Express intent to institute political reform, not specified below

0341: Express intent to change leadership

0342: Express intent to change policy

0343: Express intent to provide rights

0344: Express intent to change institutions, regime

035: Express intent to yield, not specified below

0351: Express intent to ease administrative sanctions

0352: Express intent to ease popular dissent

0353: Express intent to release persons or property

0354: Express intent to ease economic sanctions, boycott, or embargo

0355: Express intent to allow international involvement (non-mediation)

0356: Express intent to de-escalate military engagement

036: Express intent to meet or negotiate

037: Express intent to settle dispute

038: Express intent to accept mediation

039: Express intent to mediate

## 04: CONSULT

040: Consult, not specified below

041: Discuss by telephone

042: Make a visit

043: Host a visit

044: Meet at a "third" location

045: Mediate

046: Engage in negotiation

## 05: ENGAGE IN DIPLOMATIC COOPERATION

050: Engage in diplomatic cooperation, not specified below

051: Praise or endorse

052: Defend verbally

053: Rally support on behalf of

054: Grant diplomatic recognition

055: Apologize

056: Forgive

057: Sign formal agreement

## 06: ENGAGE IN MATERIAL COOPERATION

060: Engage in material cooperation, not specified below

061: Cooperate economically

062: Cooperate militarily

063: Engage in judicial cooperation

064: Share intelligence or information

## 07: PROVIDE AID

070: Provide aid, not specified below

071: Provide economic aid

072: Provide military aid

073: Provide humanitarian aid

074: Provide military protection or peacekeeping

075: Grant asylum

## 08: YIELD

080: Yield, not specified below

081: Ease administrative sanctions, not specified below

0811: Ease restrictions on political freedoms

0812: Ease ban on political parties or politicians

0813: Ease curfew

0814: Ease state of emergency or martial law

082: Ease political dissent

083: Accede to requests or demands for political reform, not specified below

0831: Accede to demands for change in leadership

0832: Accede to demands for change in policy

0833: Accede to demands for rights

0834: Accede to demands for change in institutions, regime

084: Return, release, not specified below

0841: Return, release person(s)

0842: Return, release property

085: Ease economic sanctions, boycott, embargo

086: Allow international involvement, not specified below

0861: Receive deployment of peacekeepers

0862: Receive inspectors

0863: Allow humanitarian access

087: De-escalate military engagement

0871: Declare truce, ceasefire

0872: Ease military blockade

0873: Demobilize armed forces

0874: Retreat or surrender militarily

## 09: INVESTIGATE

090: Investigate, not specified below

091: Investigate crime, corruption

092: Investigate human rights abuses

093: Investigate military action

094: Investigate war crimes

## 10: DEMAND

100: Demand, not specified below

101: Demand material cooperation, not specified below

1011: Demand economic cooperation

1012: Demand military cooperation

1013: Demand judicial cooperation

1014: Demand intelligence cooperation

102: Demand diplomatic cooperation (such as policy support)

103: Demand material aid, not specified below

1031: Demand economic aid

1032: Demand military aid

1033: Demand humanitarian aid

1034: Demand military protection or peacekeeping

104: Demand political reform, not specified below

1041: Demand change in leadership

1042: Demand policy change

1043: Demand rights

1044: Demand change in institutions, regime

105: Demand that target yields, not specified below

1051: Demand easing of administrative sanctions

1052: Demand easing of political dissent

1053: Demand release of persons or property

1054: Demand easing of economic sanctions, boycott, or embargo

1055: Demand that target allows international involvement (non-mediation)

1056: Demand de-escalation of military engagement

106: Demand meeting, negotiation

107: Demand settling of dispute

108: Demand mediation

## 11: DISAPPROVE

110: Disapprove, not specified below

111: Criticize or denounce

112: Accuse, not specified below

1121: Accuse of crime, corruption

1122: Accuse of human rights abuses

1123: Accuse of aggression

1124: Accuse of war crimes

1125: Accuse of espionage, treason

113: Rally opposition against

114: Complain officially

115: Bring lawsuit against

116: Find guilty or liable (legally)

## 12: REJECT

120: Reject, not specified below

121: Reject material cooperation

1211: Reject economic cooperation

1212: Reject military cooperation

122: Reject request or demand for material aid, not specified below

1221: Reject request for economic aid

1222: Reject request for military aid

1223: Reject request for humanitarian aid

1224: Reject request for military protection or peacekeeping

123: Reject request or demand for political reform, not specified below

1231: Reject request for change in leadership

1232: Reject request for policy change

1233: Reject request for rights

1234: Reject request for change in institutions, regime

124: Refuse to yield, not specified below

1241: Refuse to ease administrative sanctions

1242: Refuse to ease popular dissent

1243: Refuse to release persons or property

1244: Refuse to ease economic sanctions, boycott, or embargo

1245: Refuse to allow international involvement (non mediation)

1246: Refuse to de-escalate military engagement

125: Reject proposal to meet,

discuss,

or

negotiate

126: Reject mediation

127: Reject plan, agreement

to

settle

dispute

128: Defy

norms,

law

129: Veto

## 13: THREATEN

130: Threaten, not specified below

131: Threaten non-force, not specified below

1311: Threaten to reduce or stop aid

- 1312: Threate n with sanctions, boycott, embargo
- 1313: Threate n to reduce or break relations
- 132: Threate n with administrative sanctions, not specified below
- 1321: Threate n with restrictions on political freedoms
- 1322: Threate n to ban political parties or politicians
- 1323: Threate n to impose curfew
- 1324: Threate n to impose state of emergency or martial law
- 133: Threate n with political dissent, protest
- 134: Threate n to halt negotiations
- 135: Threate n to halt mediation
- 136: Threate n to halt international involvement (non-mediation)
- 137: Threate n with repression
- 138: Threate n with military force, not specified below
- 1381: Threate n blockade
- 1382: Threate n occupation
- 1383: Threate n unconventional violence
- 1384: Threate n conventional attack
- 1385: Threate n attack with WMD
- 139: Give ultimatum

## 14: PROTEST

- 140: Engage in political dissent, not specified below
- 141: Demonstrate or rally, not specified below
- 1411: Demonstrate for leadership change
- 1412: Demonstrate for policy change
- 1413: Demonstrate for rights
- 1414: Demonstrate for change in institutions, regime
- 142: Conduct hunger strike, not specified below
- 1421: Conduct hunger strike for leadership change
- 1422: Conduct hunger strike for policy change
- 1423: Conduct hunger strike for rights
- 1424: Conduct hunger strike for change in institutions, regime
- 143: Conduct strike or boycott, not specified below
- 1431: Conduct strike or boycott for leadership change
- 1432: Conduct strike or boycott for policy change
- 1433: Conduct strike or boycott for rights
- 1434: Conduct strike or boycott for change in institutions, regime
- 144: Obstruct passage, block, not specified below
- 1441: Obstruct passage to demand leadership change
- 1442: Obstruct passage to demand policy change
- 1443: Obstruct passage to demand rights
- 1444: Obstruct passage to demand change in institutions, regime
- 145: Protest violently, riot, not specified below
- 1451: Engage in violent protest for leadership change
- 1452: Engage in violent protest for policy change
- 1453: Engage in violent protest for rights
- 1454: Engage in violent protest for change in institutions, regime

## 15: EXHIBIT FORCE POSTURE

150: Demonstrate military or police power, not specified below

151: Increase police alert status

152: Increase military alert status

153: Mobilize or increase police power

154: Mobilize or increase armed forces

155: Mobilize or increase cyber-forces

## 16: REDUCE RELATIONS

160: Reduce relations, not specified below

161: Reduce or break diplomatic relations

162: Reduce or stop material aid, not specified below

1621: Reduce or stop economic assistance

1622: Reduce or stop military assistance

1623: Reduce or stop humanitarian assistance

163: Impose embargo, boycott, or sanctions

164: Halt negotiations

165: Halt mediation

166: Expel or withdraw, not specified below

1661: Expel or withdraw peacekeepers

1662: Expel or withdraw inspectors, observers

1663: Expel or withdraw aid agencies

## 17: COERCE

170: Coerce, not specified below

171: Seize or damage property, not specified below

1711: Confiscate property

1712: Destroy property

172: Impose administrative sanctions, not specified below

1721: Impose restrictions on political freedoms

1722: Ban political parties or politicians

1723: Impose curfew

1724: Impose state of emergency or martial law

173: Arrest, detain, or charge with legal action

174: Expel or deport individuals

175: Use tactics of violent repression

176: Attack cybernetically

## 18: ASSAULT

180: Use unconventional violence, not specified below

181: Abduct, hijack, or take hostage

182: Physically assault, not specified below

1821: Sexually assault

1822: Torture

1823: Kill by physical assault

1883: Conduct suicide, car, or other non-military bombing, not specified below

1831: Carry out suicide bombing

1832: Carry out vehicular bombing

1833: Carry out roadside bombing

1834: Carry out location bombing

184: Use as human shield

185: Attempt to assassinate

186: Assassinate

## 19: FIGHT

190: Use conventional military force, not specified below

191: Impose blockade, restrict movement

192: Occupy territory

193: Fight with small arms and light weapons

194: Fight with artillery and tanks

195: Employ aerial weapons, not specified below

1951: Employ precision-guided aerial munitions

1952: Employ remotely piloted aerial munitions

196: Violate ceasefire

## 20: USE UNCONVENTIONAL MASS VIOLENCE

200: Use unconventional mass violence, not specified below

201: Engage in mass expulsion

202: Engage in mass killings

203: Engage in ethnic cleansing

204: Use weapons of mass destruction, not specified below

2041: Use chemical, biological, or radiological weapons

2042: Detonate nuclear weapons

## Chapter 7

## KEDS Project Actor Codes

This is a list of all actor codes present in the dictionaries for the KEDS project, circa 2003. This alphabetically ordered list of codes can be utilized to identify different actors that might appear in TABARI outputs. "(d.r.)" denotes that the actor identified is date-restricted and is present in the dictionary under a different code for a different period. This listing now includes generic role codes however only the individual role codes are listed not the various permutations of actor and role codes. Therefore AGR (indicating an actor concerned with the field of agriculture) is listed but there are not separate listings for each XXXAGR where XXX represents a unique actor code.

Table 7.1: List of KEDS Project Actor Codes

| Code      | Actor                                                       |
|-----------|-------------------------------------------------------------|
| AFG       | Afghanistan                                                 |
| ABN       | ethnic Albanian                                             |
| ABW       | Aruba                                                       |
| AFG       | Afghanistan                                                 |
| AFGGOVTAL | Taliban (d.r.)                                              |
| AFGREBTAL | Taliban (d.r.)                                              |
| AFR       | Africa                                                      |
| AGO       | Angola                                                      |
| AGOCAB    | Cabinda Enclave                                             |
| AGOREBUNI | National Union for the Total Independence of Angola (UNITA) |
| AGR       | Agriculture (secondary role code)                           |
| AIA       | Anguilla                                                    |
| ALA       | Aland Islands                                               |
| ALB       | Albania                                                     |
| AND       | Andorra                                                     |
| ANT       | Netherlands Antilles                                        |
| ARB       | Arab (ethnic group)                                         |
| ARBTH     | Baath Party                                                 |
| ARE       | United Arab Emirates                                        |
| ARG       | Argentina                                                   |
| ARM       | Armenia                                                     |
| ASA       | Asia (region)                                               |

Continued on next page

| Code   | Actor                                                     |
|--------|-----------------------------------------------------------|
| ASM    | American Samoa                                            |
| ATG    | Antigua and Barbuda                                       |
| ATH    | Agnostic/Atheist                                          |
| AUS    | Australia                                                 |
| AUT    | Austria                                                   |
| AZE    | Azerbaijan                                                |
| BAH    | Bahai                                                     |
| BDI    | Burundi                                                   |
| BEL    | Belgium                                                   |
| BEN    | Benin                                                     |
| BFA    | Burkina Faso                                              |
| BGD    | Bangladesh                                                |
| BGR    | Bulgaria                                                  |
| BHR    | Bahrain                                                   |
| BHS    | Bahamas                                                   |
| BIH    | Bosnia and Herzegovina (d.r.)                             |
| BIHBHF | Bosniak/Croat Federation of Bosnia and Herzegovina (d.r.) |
| BIHSRP | Bosnian Serb Republika Srpska (d.r.)                      |
| BLK    | Balkans                                                   |
| BLR    | Belarus                                                   |
| BLZ    | Belize                                                    |
| BMU    | Bermuda                                                   |
| BOL    | Bolivia                                                   |
| BRA    | Brazil                                                    |
| BRB    | Barbados                                                  |
| BRN    | Brunei Darussalam                                         |
| BTN    | Bhutan                                                    |
| BUD    | Buddhist                                                  |
| BUS    | Business (secondary role code)                            |
| BWA    | Botswana                                                  |
| CAF    | Central African Republic                                  |
| CAN    | Canada                                                    |
| CAS    | Central Asia                                              |
| CAU    | Caucasus                                                  |
| CEU    | Central Europe                                            |
| CFR    | Central Africa                                            |
| CHE    | Switzerland                                               |
| CHL    | Chile                                                     |
| CHN    | China                                                     |
| CHNTIC | Tibet                                                     |
| CHR    | Christian                                                 |
| CHRCPT | Coptic                                                    |
| CHRCTH | Catholic                                                  |
| CHRDOX | Orthodox                                                  |
| CHRJHW | Jehovah's Witnesses                                       |
| CHRLDS | Latter Day Saints                                         |

| Code      | Actor                                        |
|-----------|----------------------------------------------|
| CHRMRN    | Maronite                                     |
| CHRPRO    | Protestant                                   |
| CHRRAD    | "fundamentalist" Christian                   |
| CIV       | Cte d'Ivoire (Ivory Coast)                   |
| CMN       | Communist Party                              |
| CMR       | Cameroon                                     |
| COD       | Democratic Republic of the Congo (Kinshasa)  |
| COG       | People's Republic of the Congo (Brazzaville) |
| COK       | Cook Islands                                 |
| COL       | Colombia                                     |
| COM       | Comoros                                      |
| CON       | Confucian                                    |
| COP       | Cop (primary role code)                      |
| CPV       | Cape Verde                                   |
| CRB       | Caribbean                                    |
| CRI       | Costa Rica                                   |
| CRM       | Criminal (secondary role code)               |
| CRO       | ethnic Croat                                 |
| CUB       | Cuba                                         |
| CVL       | Civilian (secondary role code)               |
| CYM       | Cayman Islands                               |
| CYP       | Cyprus                                       |
| CYPGRK    | Greek Cypriot                                |
| CYPTRK    | Turkish Cypriot                              |
| CZA       | Czechoslovakia                               |
| CZE       | Czech Republic                               |
| DEV       | Development (secondary role code)            |
| DEU       | Germany                                      |
| DJI       | Djibouti                                     |
| DMA       | Dominica                                     |
| DNK       | Denmark                                      |
| DOM       | Dominican Republic                           |
| DZA       | Algeria                                      |
| DZAGOVFLN | National Liberation Front (FLN)              |
| DZAGOVMSP | Movement of the Society for Peace            |
| DZAGOVRND | Democratic National Rally                    |
| DZAOPPENN | Ennahda Movement                             |
| DZAOPPFIS | Islamic Salvation Front                      |
| DZAOPPFLN | National Liberation Front (FLN)              |
| DZAOPPMSP | Movement of the Society for Peace            |
| DZAREBFIS | Islamic Salvation Army                       |
| DZAREBGIA | Armed Islamic Group (GIA)                    |
| DZAREBGP  | Salafist Group                               |
| EAF       | Eastern Africa                               |
| ECU       | Ecuador                                      |
| EDU       | Education (secondary role code)              |

| Code      | Actor                                        |
|-----------|----------------------------------------------|
| EEU       | Eastern Europe                               |
| EGY       | Egypt                                        |
| EGYREMBR  | Muslim Brotherhood                           |
| EIN       | East Indies (region)                         |
| ELI       | Elites (secondary role code)                 |
| ENV       | Environment (secondary role code)            |
| ERI       | Eritrea                                      |
| ESH       | Western Sahara                               |
| ESP       | Spain                                        |
| ESPBSQ    | Basque                                       |
| EST       | Estonia                                      |
| ETH       | Ethiopia                                     |
| EUR       | Europe                                       |
| FIN       | Finland                                      |
| FJI       | Fiji                                         |
| FLK       | Falkland Islands (Malvinas)                  |
| FRA       | France                                       |
| FRO       | Faeroe Islands                               |
| FRY       | Federal Republic of Yugoslavia               |
| FRYKSV    | Kosovo (d.r.)                                |
| FRYMTN    | Montenegro (d.r.)                            |
| FRYSRB    | Serbia (d.r.)                                |
| FRYVVD    | Vojvodina (d.r.)                             |
| FSM       | Micronesia                                   |
| GAB       | Gabon                                        |
| GBR       | United Kingdom                               |
| GBRREBIRA | Irish Republican Army                        |
| GEO       | Georgia                                      |
| GHA       | Ghana                                        |
| GIB       | Gibraltar                                    |
| GIN       | Guinea                                       |
| GLP       | Guadeloupe                                   |
| GMB       | Gambia                                       |
| GME       | Democratic Republic of Germany (East Berlin) |
| GMW       | Federal Republic of Germany (Bonn)           |
| GNB       | Guinea-Bissau                                |
| GNQ       | Equatorial Guinea                            |
| GOV       | Government (primary role code                |
| GRC       | Greece                                       |
| GRD       | Grenada                                      |
| GRL       | Greenland                                    |
| GTM       | Guatemala                                    |
| GUF       | French Guiana                                |
| GUM       | Guam                                         |
| GUY       | Guyana                                       |
| GYP       | Gypsy                                        |

| Code         | Actor                                                      |
|--------------|------------------------------------------------------------|
| HIN          | Hindu                                                      |
| HKG          | Hong Kong (Special Administrative Region of China)         |
| HLH          | Health (secondary role code)                               |
| HND          | Honduras                                                   |
| HRV          | Croatia (d.r.)                                             |
| HTI          | Haiti                                                      |
| HUN          | Hungary                                                    |
| HUT          | Hutu (ethnic group)                                        |
| IDN          | Indonesia                                                  |
| IGO          | Inter-governmental organizations                           |
| IGOAGRCPA    | Cocoa Producer's Alliance                                  |
| IGOAGRCPC    | Association of Coffee Producing Countries                  |
| IGOAGRICO    | International Cocoa Organization (ICCO)                    |
| IGOAGRIGC    | International Grains Council                               |
| IGOAFRAFU    | African Union                                              |
| IGOAFRAGRIAC | Inter-African Coffee Organization (IACO)                   |
| IGOAFRBUSCES | Common Market for Eastern and Southern Africa              |
| IGOAFRBUSCFA | Franc Zone Financial Community of Africa                   |
| IGOAFRDEVAFB | African Development Bank                                   |
| IGOAFRDEVATD | Eastern and Southern African Trade and Development Bank    |
| IGOAFRDEVNEP | New Economic Partnership for Africa's Development          |
| IGOAFROAU    | Organization of African Unity (OAU)                        |
| IGOAFRPAP    | Pan African Parliament                                     |
| IGOARBAPE    | Organization of Arab Petroleum Exporting Countries (OAPEC) |
| IGOARBDEVABD | Arab Bank for Economic Development in Africa               |
| IGOBUSBIS    | Bank for International Settlements                         |
| IGOBUSGOE    | Group of Eight (G-8)                                       |
| IGOBUSGOS    | Group of Seven (G-7)                                       |
| IGOBUSGSS    | Group of Seventy-Seven (G-77)                              |
| IGOBUSHIP    | Highly Indebted Poor Countries (HIPC)                      |
| IGOBUSIMF    | International Monetary Fund (IMF)                          |
| IGOBUSOPC    | Organization of Petroleum Exporting Countries (OPEC)       |
| IGOBUSPROC   | Paris Club                                                 |
| IGOBUSWTO    | World Trade Organization (WTO)                             |
| IGOCAFBCA    | Bank of Central African States (BEAC)                      |
| IGOCAFECA    | Economic Community of Central African States               |
| IGOCAFCEM    | Monetary and Economic Community of Central Africa (CEMAC)  |
| IGOASCIS     | Commonwealth of Independent States                         |
| IGOCOPITP    | Interpol                                                   |
| IGOCWN       | Commonwealth of Nations                                    |
| IGOEAFDEVIAD | Intergovernmental Authority on Development (IGAD)          |
| IGOEAFEAC    | East African Community                                     |
| IGOEURBUSEFT | European Free Trade Association                            |
| IGOEURCOE    | Council of Europe                                          |
| IGOEURDEVEBR | European Bank for Reconstruction and Development           |
| IGOEUREEC    | European Union                                             |

| Code         | Actor                                                   |
|--------------|---------------------------------------------------------|
| IGOEURSCE    | Council of Security and Cooperation in Europe (OSEC)    |
| IGOJUDICC    | International Criminal Court                            |
| IGOLEGIPU    | Inter-Parliamentary Union                               |
| IGOMEAAEU    | Arab Economic Unity Council                             |
| IGOMEAAACC   | Arab Cooperation Council                                |
| IGOMEAAMF    | Arab Monetary Fund for Economic and Social Development  |
| IGOMEAMU     | Arab Maghreb Union                                      |
| IGOMEAARL    | Arab League                                             |
| IGOMOSDEVIDB | Islamic Development Bank                                |
| IGOMOSOIC    | Organization of Islamic Conferences (OIC)               |
| IGONAFCSS    | Community of Sahel-Saharan States (CENSAD)              |
| IGONON       | Organization of Non-Aligned Countries                   |
| IGOOAS       | Organization of American States                         |
| IGOPGSGCC    | Gulf Cooperation Council                                |
| IGOPKO       | Peacekeeping force (organization unknown)               |
| IGOSAFDEVSAD | Southern African Development Community                  |
| IGOSASSAA    | South Asian Association                                 |
| IGOSEAASN    | Association of Southeast Asian Nations (ASEAN)          |
| IGOSEASOT    | Southeast Asia Collective Defense Treaty (SEATO)        |
| IGOSEADEVADB | Asian Development Bank                                  |
| IGOUNO       | United Nations                                          |
| IGOUNOAGRFAO | United Nations Food and Agriculture Organization        |
| IGOUNOAIE    | International Energy Agency                             |
| IGOUNODEVWBK | The World Bank                                          |
| IGOUNOHLHWHO | World Health Organization (WHO)                         |
| IGOUNOHRIHCH | United Nations High Commission for Human Rights (OHCHR) |
| IGOUNOIAE    | International Atomic Energy Agency (IAEA)               |
| IGOUNOJUDICJ | International Court of Justice (ICJ)                    |
| IGOUNOJUDWCT | International War Crimes Tribunals                      |
| IGOUNOKID    | United Nations Children's Fund (UNICEF)                 |
| IGOUNOLABILO | International Labor Organization                        |
| IGOUNOREFCHR | United Nations High Commission for Refugees (OHCR)      |
| IGOUNOWFP    | World Food Program                                      |
| IGOWAFDEVWAM | West Africa Monetary and Economic Union                 |
| IGOWAFUEM    | Economic and Monetary Union of West Africa (UEMOA)      |
| IGOWAFWAD    | West Africa Development Bank                            |
| IGOWAFWAS    | Economic Community of West African States (ECOWAS)      |
| IGOWEU       | Western European Union                                  |
| IGOWSTNAT    | North Atlantic Treaty Organization (NATO)               |
| IMGMOSALQ    | Al Qaeda                                                |
| IMGSEAMOSASF | Abu Sayyaf                                              |
| IMGSEAMOSJMA | Jemaah Islamiya                                         |
| IMY          | Isle of Man                                             |
| IND          | India                                                   |
| INDKAS       | Indian-controlled Kashmir                               |
| INT          | Ambiguous international or transnational actor          |

| Code       | Actor                          |
|------------|--------------------------------|
| IRL        | Ireland                        |
| IRN        | Iran                           |
| IRQ        | Iraq                           |
| IRQBAG     | Baghdad                        |
| IRQKURKDP  | Kurdish Democratic Party (KDP) |
| ISL        | Iceland                        |
| ISR        | Israel                         |
| ISRGOVCMN  | Israeli Communist Party (d.r.) |
| ISRGOVLBA  | Israeli Labor Party (d.r.)     |
| ISRGOVLKD  | Likud Party (d.r.)             |
| ISRGOVMRZ  | Meretz Party (d.r.)            |
| ISRGOVSHA  | Shas Party (d.r.)              |
| ISRGOVCMN  | Israeli Communist Party (d.r.) |
| ISROPPLBA  | Israeli Labor Party (d.r.)     |
| ISROPPLKD  | Likud Party (d.r.)             |
| ISROPPMRZ  | Meretz Party (d.r.)            |
| ISROPPSHA  | Shas Party (d.r.)              |
| ISRSET     | Israeli Settlers               |
| ITA        | Italy                          |
| JAM        | Jamaica                        |
| JAN        | Jain                           |
| JEW        | Jew                            |
| JEWHSD     | Hasidic Jew                    |
| JEWUDX     | Ultra-Orthodox Jew             |
| JOR        | Jordan                         |
| JOROPPIAF  | Islamic Action Front           |
| JPN        | Japan                          |
| JUD        | Judiciary (primary role code)  |
| KAS        | Kashmir                        |
| KAZ        | Kazakhstan                     |
| KEN        | Kenya                          |
| KGZ        | Kyrgyzstan                     |
| KHM        | Cambodia                       |
| KHMREBKMRA | Khmer Rouge                    |
| KIR        | Kiribati                       |
| KNA        | Saint Kitts-Nevis              |
| KOR        | Republic of Korea (Seoul)      |
| KUR        | Kurd (ethnic group)            |
| KWT        | Kuwait                         |
| LAB        | Labor (secondary role code)    |
| LAM        | Latin America                  |
| LAO        | Laos                           |
| LBN        | Lebanon                        |
| LBNREBAML  | Amal Militia                   |
| LBNREBASL  | South Lebanon Army             |
| LBNREBHEZ  | Hezbollah                      |

| Code      | Actor                                                    |
|-----------|----------------------------------------------------------|
| LBR       | Liberia                                                  |
| LBRBOM    | Bomi (Liberia)                                           |
| LBRBON    | Bong (Liberia)                                           |
| LBRCAP    | Grand Cape Mount (Liberia)                               |
| LBRGBA    | Grand Bassa (Liberia)                                    |
| LBRGGC    | Grand Gedeh (Liberia)                                    |
| LBRGOVLAP | Liberia Action Party (d.r.)                              |
| LBRGOVNDP | National Democratic Party of Liberia (d.r.)              |
| LBRGOVNPF | National Patriotic Front of Liberia (NPFL) (d.r.)        |
| LBRGOVUPP | United People's Party (d.r.)                             |
| LBRKRH    | Krahn (ethnic group)                                     |
| LBRKRU    | Grand Kru (Liberia)                                      |
| LBRLOF    | Lofa (Liberia)                                           |
| LBRMAN    | Mandingo, Mandingo (ethnic group)                        |
| LBRMNT    | Montserrat (Liberia)                                     |
| LBRMRG    | Margibi (Liberia)                                        |
| LBRMRY    | Maryland (Liberia)                                       |
| LBRNIM    | Nimba (Liberia)                                          |
| LBROPPALC | All Liberia Coalition Party                              |
| LBROPPLAP | Liberia Action Party (d.r.)                              |
| LBROPPNDM | New Deal Movement                                        |
| LBROPPNDP | National Democratic Party of Liberia (d.r.)              |
| LBROPPUPP | United People's Party (d.r.)                             |
| LBRREBAFL | Armed Forces of Liberia (d.r.)                           |
| LBRREBINP | Independent NPFL                                         |
| LBRREBLPC | Liberia Peace Council                                    |
| LBRREBLUR | Liberians United for Reconciliation and Democracy (LURD) |
| LBRREBNPF | National Patriotic Front of Liberia (NPFL) (d.r.)        |
| LBRREBULM | United Liberation Front for Democracy                    |
| LBRRVC    | Rivercess (Liberia)                                      |
| LBRSIN    | Sino (Liberia)                                           |
| LBY       | Libya                                                    |
| LCA       | Saint Lucia                                              |
| LEG       | Legislature (secondary role code)                        |
| LIE       | Liechtenstein                                            |
| LKA       | Sri Lanka                                                |
| LKAREBJVP | People's Liberation Front                                |
| LSO       | Lesotho                                                  |
| LTU       | Lithuania                                                |
| LUX       | Luxembourg                                               |
| LVA       | Latvia                                                   |
| MAC       | Macao (Special Administrative Region of China)           |
| MAR       | Morocco                                                  |
| MARREBPLS | Polisario Guerillas                                      |
| MCO       | Monaco                                                   |
| MDA       | Moldova                                                  |

| Code   | Actor                                           |
|--------|-------------------------------------------------|
| MDG    | Madagascar                                      |
| MDT    | Mediterranean                                   |
| MDV    | Maldives                                        |
| MEA    | Middle East                                     |
| MED    | Medical (secondary role code)                   |
| MEX    | Mexico                                          |
| MHL    | Marshall Islands                                |
| MIL    | MII lary (primary role code)                    |
| MKD    | Macedonia                                       |
| MLI    | Mali                                            |
| MLT    | Malta                                           |
| MMR    | Myanmar (Burma)                                 |
| MNC    | Multi-national corporation                      |
| MNG    | Mongolia                                        |
| MNP    | Northern Mariana Islands                        |
| MOD    | Moderate (tertiary role code)                   |
| MOS    | Muslim                                          |
| MOSALE | Alewi                                           |
| MOSDRZ | Druze                                           |
| MOSRAD | "Fundamentalist," "radical," "extremist" Muslim |
| MOSSFI | Sufi                                            |
| MOSSHI | Shia                                            |
| MOSSUN | Sunni                                           |
| MOZ    | Mozambique                                      |
| MRT    | Mauritania                                      |
| MSR    | Montserrat                                      |
| MTN    | Montenegro                                      |
| MTQ    | Martinique                                      |
| MUS    | Mauritius                                       |
| MWI    | Malawi                                          |
| MYS    | Malaysia                                        |
| MYT    | Mayotte                                         |
| NAF    | North Africa                                    |
| NAM    | Namibia                                         |
| NCL    | New Caledonia                                   |
| NER    | Niger                                           |
| NFK    | Norfolk Island                                  |
| NGA    | Nigeria                                         |
| NGAABI | Abia (Nigeria)                                  |
| NGAABU | Abuja (Nigeria)                                 |
| NGAADA | Adamawa (Nigeria)                               |
| NGAAKI | Akwa Ibom (Nigeria)                             |
| NGAANB | Anambra (Nigeria)                               |
| NGABAU | Bauchi (Nigeria)                                |
| NGABAY | Bayelsa (Nigeria)                               |
| NGABIA | Biafra (Nigeria)                                |

| Code      | Actor                                                   |
|-----------|---------------------------------------------------------|
| NGABNU    | Benue (Nigeria)                                         |
| NGABOR    | Borno (Nigeria)                                         |
| NGACRR    | Cross River (Nigeria)                                   |
| NGADEL    | Delta (Nigeria)                                         |
| NGAEBO    | Edo (Nigeria)                                           |
| NGAEKI    | Ekiti (Nigeria)                                         |
| NGAENU    | Enugu (Nigeria)                                         |
| NGAGOM    | Gombe (Nigeria)                                         |
| NGAHAU    | Hausa (ethnic group)                                    |
| NGAIBO    | Ibo, Igbo (ethnic group)                                |
| NGAIJW    | Ijaws (ethnic group)                                    |
| NGAIMO    | Imo (Nigeria)                                           |
| NGAJIG    | Jigawa (Nigeria)                                        |
| NGAKAD    | Kaduna (Nigeria)                                        |
| NGAKAN    | Kano (Nigeria)                                          |
| NGAKAT    | Katsina (Nigeria)                                       |
| NGAKEB    | Kebbi (Nigeria)                                         |
| NGAKOG    | Kogi (Nigeria)                                          |
| NGAKWA    | Kwara (Nigeria)                                         |
| NGALAG    | Lagos (Nigeria)                                         |
| NGANAS    | Nassarawa (Nigeria)                                     |
| NGANDR    | Niger Delta Region (Nigeria)                            |
| NGANGR    | Niger (Nigeria)                                         |
| NGANNG    | North Nigeria (Nigeria)                                 |
| NGAOGO    | Ogoni (ethnic group)                                    |
| NGAOGU    | Ogun (Nigeria)                                          |
| NGAOND    | Ondo (Nigeria)                                          |
| NGAOPPANP | All Nigeria People's Party                              |
| NGAOPPCFD | Campaign for Democracy                                  |
| NGAOPPNDC | National Democratic Coalition of Nigeria (NADECO)       |
| NGAOSU    | Osun (Nigeria)                                          |
| NGAOYO    | Oyo (Nigeria)                                           |
| NGAPLA    | Plateu State (Nigeria)                                  |
| NGAREBMAD | Movement for the Advancement of Democracy (MAD)         |
| NGARIV    | Rivers (Nigeria)                                        |
| NGASOK    | Sokoto (Nigeria)                                        |
| NGATAR    | Taraba (Nigeria)                                        |
| NGATIV    | Tiv (ethnic group, language)                            |
| NGAYOB    | Yobe (Nigeria)                                          |
| NGAYRB    | Yoruba (ethnic group)                                   |
| NGAZAM    | Zamfara (Nigeria)                                       |
| NGM       | Non-governmental movements                              |
| NGMGRP    | Greenpeace                                              |
| NGO       | Non-governmental organizations                          |
| NGOCHRCSI | Christian Solidarity International                      |
| NGOHLHCRC | International Fed. of Red Cross and Red Crescent (ICRC) |

| Code       | Actor                                              |
|------------|----------------------------------------------------|
| NGOHLHIRC  | Red Cross                                          |
| NGOHLHMSF  | Medecins Sans Frontieres (Doctors Without Borders) |
| NGOHLHRCR  | Red Crescent                                       |
| NGOHRIAMN  | Amnesty International                              |
| NGOHRIFID  | International Federation of Human Rights (FIDH)    |
| NGOHRIHRW  | Human Rights Watch                                 |
| NGOHRIIIHF | International Helsinki Federation for Human Rights |
| NGOICG     | International Crisis Group                         |
| NGOJUDJUR  | International Commission of Jurists                |
| NGOREFIONM | International Organization for Migration           |
| NGOUAJ     | Union of Arab Journalists                          |
| NGOWEF     | World Economic Forum                               |
| NGOXFM     | Oxfam                                              |
| NIC        | Nicaragua                                          |
| NIU        | Niue                                               |
| NLD        | Netherlands                                        |
| NMR        | North America                                      |
| NOR        | Norway                                             |
| NPL        | Nepal                                              |
| NRU        | Nauru                                              |
| NZL        | New Zealand                                        |
| OMN        | Oman                                               |
| OPP        | Opposition (primary role code)                     |
| PAG        | Animist/Pagan                                      |
| PAK        | Pakistan                                           |
| PAKKAS     | Pakistani-controlled Kashmir                       |
| PAL        | Palestinian                                        |
| PALPLO     | Palestine Liberation Organization                  |
| PALREBANO  | Abu Nidal Organization                             |
| PALREBPLF  | Palestine Liberation Front                         |
| PAN        | Panama                                             |
| PCN        | Pitcairn                                           |
| PER        | Peru                                               |
| PGS        | Persian Gulf                                       |
| PHL        | Philippines                                        |
| PLW        | Palau                                              |
| PNG        | Papua New Guinea                                   |
| PNGBOU     | Bougainville                                       |
| POL        | Poland                                             |
| PRI        | Puerto Rico                                        |
| PRK        | Democratic People's Rep. of Korea (Pyongyang)      |
| PRT        | Portugal                                           |
| PRY        | Paraguay                                           |
| PSE        | Palestinian Occupied Territories                   |
| PSEGOVFTA  | Fatah (d.r.)                                       |
| PSEGOVHMS  | Hamas (d.r.)                                       |

| Code       | Actor                                                   |
|------------|---------------------------------------------------------|
| PSEGZS     | Gaza Strip                                              |
| PSEREBAAIM | Al Aqsa Martyrs Brigade                                 |
| PSEREBDFL  | Democratic Front for the Liberation of Palestine (DFLP) |
| PSEREBHMS  | Hamas (d.r.)                                            |
| PSEREBISJ  | Palestinian Islamic Jihad                               |
| PSEREBPFL  | People's Front for the Liberation of Palestine (PFLP)   |
| PSEWSB     | West Bank                                               |
| PYF        | French Polynesia                                        |
| QAT        | Qatar                                                   |
| RAD        | Radical (tertiary role code)                            |
| REB        | Rebel (primary role code)                               |
| REF        | Refugee (secondary role code)                           |
| REU        | Runion                                                  |
| ROM        | Romania                                                 |
| RUS        | Russia                                                  |
| RUSCNY     | Chechnya                                                |
| RWA        | Rwanda                                                  |
| RWAGOVRPF  | Rwandan Patriotic Front (d.r.)                          |
| RWAUAFRPF  | Rwandan Patriotic Front (d.r.)                          |
| SAF        | Southern Africa                                         |
| SAM        | South America                                           |
| SAS        | South Asia                                              |
| SAU        | Saudi Arabia                                            |
| SCG        | Serbia and Montenegro (d.r.)                            |
| SCGKSV     | Kosovo (d.r.)                                           |
| SCGMTN     | Montenegro (d.r.)                                       |
| SCGSRB     | Serbia (d.r.)                                           |
| SCGVVD     | Vojvodina (d.r.)                                        |
| SCN        | Scandinavia                                             |
| SDN        | Sudan                                                   |
| SDNDFR     | Darfur                                                  |
| SDNREBNDA  | National Democratic Alliance                            |
| SDNREBSPL  | Sudan People's Liberation Army                          |
| SEA        | Southeast Asia                                          |
| SEN        | Senegal                                                 |
| SENREBMDF  | Movement of Democratic Forces of Casamance              |
| SER        | ethnic Serb                                             |
| SGP        | Singapore                                               |
| SHN        | Saint Helena                                            |
| SIK        | Sikh                                                    |
| SJM        | Svalbard and Jan Mayen Islands                          |
| SLA        | Slav                                                    |
| SLB        | Solomon Islands                                         |
| SLE        | Sierra Leone                                            |
| SLEREBKAM  | Kamojor militia                                         |
| SLEREBRUF  | Revolutionary United Front                              |

| Code      | Actor                                           |
|-----------|-------------------------------------------------|
| SLV       | El Salvador                                     |
| SMR       | San Marino                                      |
| SNL       | Sinhalese (ethnic group)                        |
| SOM       | Somalia                                         |
| SPM       | Saint Pierre and Miquelon                       |
| SPY       | Spy (primary role code)                         |
| SRB       | Serbia (d.r.)                                   |
| SRBKSV    | Kosovo (d.r.)                                   |
| SRBVVD    | Vojvodina (d.r.)                                |
| STP       | Sao Tome and Principe                           |
| SUR       | Suriname                                        |
| SVK       | Slovakia                                        |
| SVN       | Slovenia                                        |
| SWE       | Sweden                                          |
| SWZ       | Swaziland                                       |
| SYC       | Seychelles                                      |
| SYR       | Syria                                           |
| TAM       | Tamil (ethnic group)                            |
| TAO       | Taoist                                          |
| TCA       | Turks and Caicos Islands                        |
| TCD       | Chad                                            |
| TER       | Terai (region in northern India/southern Nepal) |
| TGO       | Togo                                            |
| THA       | Thailand                                        |
| TJK       | Tajikistan                                      |
| TKL       | Tokelau                                         |
| TKM       | Turkmenistan                                    |
| TMP       | East Timor (Timor-Leste)                        |
| TON       | Tonga                                           |
| TRG       | Tuareg (ethnic group)                           |
| TRK       | ethnic Turk                                     |
| TTO       | Trinidad and Tobago                             |
| TUN       | Tunisia                                         |
| TUR       | Turkey                                          |
| TURANK    | Ankara                                          |
| TURGOVAKP | Justice and Development Party (AKP) (d.r.)      |
| TURGOVANP | Motherland Party (ANAP) (d.r.)                  |
| TURGOVCHP | Republican People's Party (CHP) (d.r.)          |
| TURGOVDSP | Democratic Left Party (DSP) (d.r.)              |
| TURGOVDP  | True Path Party (DYP) (d.r.)                    |
| TURGOVMHP | National Action Party (MHP) (d.r.)              |
| TURGOVREP | Welfare Party (Refah) (d.r.)                    |
| TURIST    | Istanbul                                        |
| TURIZM    | Izmir                                           |
| TUROPPAKP | Justice and Development Party (AKP) (d.r.)      |
| TUROPPANP | Motherland Party (ANAP) (d.r.)                  |

| Code      | Actor                                           |
|-----------|-------------------------------------------------|
| TUROPPCHP | Republican People's Party (CHP) (d.r.)          |
| TUROPPDSP | Democratic Left Party (DSP) (d.r.)              |
| TUROPPDTP | Democratic Society Party (DTP)                  |
| TUROPPDYP | True Path Party (DYP) (d.r.)                    |
| TUROPPFAZ | Virtue Party (Fazilet)                          |
| TUROPPHDP | Democratic People's Party (DEHAP/HADEP)         |
| TUROPPMHP | National Action Party (MHP) (d.r.)              |
| TUROPPREP | Welfare Party (Refah) (d.r.)                    |
| TURREBDSL | Dev-Sol                                         |
| TURREBPKK | Kurdistan Workers' Party (PKK)                  |
| TURSOE    | Southeast Turkey                                |
| TUT       | Tutsi (ethnic group)                            |
| TUV       | Tuvalu                                          |
| TWN       | Taiwan                                          |
| TZA       | Tanzania                                        |
| UAF       | Unidentified Armed Force (tertiary role code)   |
| UGA       | Uganda                                          |
| UGAREBADF | Allied Democratic Forces                        |
| UGAREBLRA | Lord's Resistance Army                          |
| UIG       | Uighur (Chinese ethnic minority)                |
| UIS       | Unidentified state actors                       |
| UKR       | Ukraine                                         |
| URY       | Uruguay                                         |
| USA       | United States                                   |
| USR       | Union of Soviet Socialist Republics (USSR)      |
| UZB       | Uzbekistan                                      |
| VAT       | Holy See (Vatican City)                         |
| VCT       | Saint Vincent and the Grenadines                |
| VEN       | Venezuela                                       |
| VGB       | British Virgin Islands                          |
| VIR       | U.S. Virgin Islands                             |
| VNM       | Vietnam                                         |
| VUT       | Vanuatu                                         |
| WAF       | West Africa                                     |
| WLF       | Wallis and Futuna Islands                       |
| WSM       | Samoa                                           |
| WST       | "the West"                                      |
| YEM       | Yemen                                           |
| YMN       | North Yemen                                     |
| YMS       | South Yemen                                     |
| YUG       | Socialist Federal Republic of Yugoslavia (d.r.) |
| YUGBSN    | Yugoslavia's Republic of Bosnia (d.r.)          |
| YUGCTA    | Yugoslavia's Republic of Croatia (d.r.)         |
| YUGKSV    | Kosovo (d.r.)                                   |
| YUGMCD    | Yugoslavia's Republic of Macedonia (d.r.)       |
| YUGMTN    | Montenegro (d.r.)                               |

| Code   | Actor                                    |
|--------|------------------------------------------|
| YUGSLN | Yugoslavia's Republic of Slovenia (d.r.) |
| YUGSRB | Yugoslavia's Republic of Serbia (d.r.)   |
| YUGVVD | Vojvodina (d.r.)                         |
| ZAF    | South Africa                             |
| ZMB    | Zambia                                   |
| ZRO    | Zoroastrian                              |
| ZWE    | Zimbabwe                                 |

## Chapter 8

## CAMEO Religious Classification System

The comprehensive list of all religious codes is arranged by its subsections as follows: first into named religions, followed by religious categories, each alphabetically arranged; second alphabetically; and third, numerically. The newest version of the CAMEORCS directory will be made available on http://cameocodes.wikispaces.com/ .

The current version is 0.1.1, finalized on May 27, 2011.

Table 8.1: Directory of all Religious Codes (v.1.0)

| Heirarchical Code   | Religion and Comments                                                                   |
|---------------------|-----------------------------------------------------------------------------------------|
| REL                 | Unspecified Religious                                                                   |
| ATH                 | Agnostic/Atheist Freethought                                                            |
| ATH010              | Bahai Faith inc. all non-schismatic Bahai                                               |
| BAH                 | Baha'is Under the Provisions of the Covenant                                            |
| BAH020              | Faith of God a.k.a. the House of Mankind and the Universal Palace of Order              |
| BAH030              | Free Baha'i Faith                                                                       |
| BAH040              | Orthodox Baha'i Faith a.k.a. Mother Baha'i Council                                      |
| BAH050              | Orthodox Baha'i Faith Under the Regency                                                 |
| BAH060              | Charles Mason Remey Society                                                             |
| BAH070              | The Friends Newsletter                                                                  |
| BUD                 | Buddhism                                                                                |
| BUDMAH              | Mahayana Buddhism                                                                       |
| BUDMAH100           | Pure Land Buddhism a.k.a. Amidism                                                       |
| BUDMAH110           | Jodo Shinshu a.k.a. Shin Buddhism                                                       |
| BUDMAH111           | Hongan-ji School a.k.a. Jodo Shinshu Hompa Hongwanji-ha, Nishi Hongan-ji                |
| BUDMAH112           | Otani School a.k.a. Jodo Shinshu Otani-ha, Higashi Hongan-ji                            |
| BUDMAH113           | Takada School                                                                           |
| BUDMAH114           | Bukkoji School                                                                          |
| BUDMAH115           | Kosho School                                                                            |
| BUDMAH116           | Kibe School                                                                             |
| BUDMAH117           | Izumoji School                                                                          |
| BUDMAH118           | Joshiyo School                                                                          |
| BUDMAH120           | Jodo Shu (mainline group: "Chinzei" branch)                                             |
| BUDMAH121           | Seizan branch                                                                           |
| BUDMAH130           | Vietnamese Pure Land Buddhism (specifically, Vietnamese Pure Land Buddhism Association) |
| BUDMAH140           | Yuzu Nembutsu                                                                           |
| BUDMAH200           | Zen Buddhism a.k.a. Chan Buddhism                                                       |
| BUDMAH210           | Classic Zen                                                                             |
| BUDMAH211           | Caodong school inc. Soto sect (Japanese line)                                           |
| BUDMAH212           | Fayan school                                                                            |
| BUDMAH213           | Guiyang school                                                                          |
| BUDMAH214           | Linji school inc. Rinzai school (Japanese line)                                         |
| BUDMAH215           | Yunmen school                                                                           |
| BUDMAH220           | Japanese Zen (excluding classical schools)                                              |
| BUDMAH221           | Obaku                                                                                   |
| BUDMAH223           | Soto                                                                                    |
| BUDMAH230           | Seon Buddhism a.k.a. Korean Zen                                                         |
| BUDMAH231           | Jogye Order                                                                             |
| BUDMAH240           | Thien Tong a.k.a. Thien Buddhism, Vietnamese Zen                                        |
| BUDMAH300           | Nichiren Buddhism (note that a number of names are shared by multiple schools/sects)    |
| BUDMAH301           | Fuji Taisekiji Kenshokai                                                                |

| Heirarchical Code   | Religion and Comments                                                                                    |
|---------------------|----------------------------------------------------------------------------------------------------------|
| BUDMAH302           | Fuju-fuse Nichiren Komon Shu                                                                             |
| BUDMAH303           | Hokke Nichiren Shu                                                                                       |
| BUDMAH304           | Hokkeshu                                                                                                 |
| BUDMAH305           | Hompa Nichiren Shu                                                                                       |
| BUDMAH306           | Honke Nichiren Shu                                                                                       |
| BUDMAH307           | Honmon Butsuryu Shu Ja                                                                                   |
| BUDMAH308           | Honmon Hokke Shu                                                                                         |
| BUDMAH309           | Honmon Kyoo Shu                                                                                          |
| BUDMAH310           | Honm Shoshu                                                                                              |
| BUDMAH311           | Kempon Hokke Shu                                                                                         |
| BUDMAH312           | Kokuchukai- a.k.a. Kokuchukai ja                                                                         |
| BUDMAH313           | Nichiren Hokke Shu                                                                                       |
| BUDMAH314           | Nichiren Honshu                                                                                          |
| BUDMAH315           | Nichiren Komon Shu                                                                                       |
| BUDMAH316           | Nichiren Shoshu                                                                                          |
| BUDMAH317           | Nichiren Shu                                                                                             |
| BUDMAH318           | Nichiren Shu Fuji-fuse-ha a.s.a. Nichirenshu Fuji-fuse-ha                                                |
| BUDMAH319           | Nipponzan Myohoji                                                                                        |
| BUDMAH320           | Reiyukai a.k.a. Spiritual-Friendship-Association                                                         |
| BUDMAH321           | Risso Kosei Kai                                                                                          |
| BUDMAH322           | Shobo Hokke Shu                                                                                          |
| BUDMAH323           | Shoshinkai                                                                                               |
| BUDMAH324           | Soka Gakkai                                                                                              |
| BUDMAH400           | Tiantai and regional variants thereof                                                                    |
| BUDMAH410           | Cheontae                                                                                                 |
| BUDMAH420           | Tendai                                                                                                   |
| BUDMAH500           | Shinnyo-en                                                                                               |
| BUDMLN              | millenarian Buddhist movements                                                                           |
| BUDMLN010           | Aum Shinrikyo a.k.a. Aleph                                                                               |
| BUDMLN011           | Hikari No Wa                                                                                             |
| BUDNRM              | new Buddhist movements                                                                                   |
| BUDNRM010           | Santi Asoke                                                                                              |
| BUDSYN              | syncretic Buddhism                                                                                       |
| BUDSYN010           | Tara Center                                                                                              |
| BUDTHR              | Therevada Buddhism                                                                                       |
| BUDTHR400 (+500     | Therevada monastic orders                                                                                |
| BUDTHR410           | Amarapura Nikaya                                                                                         |
| BUDTHR420           | Dhammayuttika Nikaya                                                                                     |
| BUDTHR430           | Dvara Nikaya                                                                                             |
| BUDTHR440           | Maha Nikaya                                                                                              |
| BUDTHR441           | Dhammakaya Movement                                                                                      |
| BUDTHR450           | Mahasthabir Nikaya                                                                                       |
| BUDTHR460           | Ramanna Nikaya                                                                                           |
| BUDTHR470           | Sangharaj Nikaya                                                                                         |
| BUDTHR480           | Shwekyin Nikaya                                                                                          |
| BUDTHR490           | Siam Nikaya                                                                                              |
| BUDTHR500           | Thudhamma Nikaya                                                                                         |
| BUDVAJ              | Vajrayana Buddhism a.k.a. Tantra, Diamond Vehicle, Esoteric Buddhism,                                    |
| BUDVAJ100           | Newar Buddhism                                                                                           |
| BUDVAJ200           | Shingon Buddhism a.k.a. Orthodox Esoteric Buddhism, Japanese Esoteric Buddhism                           |
| BUDVAJ210           | Kogi Shingon School a.k.a. Ancient Shingon School                                                        |
| BUDVAJ220           | Shingon School a.k.a. Reformed Shingon School                                                            |
| BUDVAJ300           | Shugendo                                                                                                 |
| BUDVAJ400           | Tibetan Buddhism (N.B. all forms of Tibetan Buddhism other than Gelug are called "Red Hat sects")        |
| BUDVAJ410           | Gelug a.k.a. Gelug-pa, dGe Lugs Pa, dge-lugs-pa, Dgelugspa, Yellow Hat Sect; includes Dalai Lama         |
| BUDVAJ420           | Kagyu a.k.a. Kaguya, Kagyud                                                                              |
| BUDVAJ421           | Barom Kagyu                                                                                              |
| BUDVAJ422           | Drubgyu Karma Kamtsang a.k.a. Karma Kagyu, Karma Kamtsang, Karmapa Sect                                  |
| BUDVAJ423           | Drikung Kagyu                                                                                            |
| BUDVAJ424           | Drukpa Kagyu                                                                                             |
| BUDVAJ425           | Shangpa Kagyu                                                                                            |
| BUDVAJ426           | Taklung Kagyu                                                                                            |
| BUDVAJ430           | Nyingma a.k.a. Nyingmaapa                                                                                |
| BUDVAJ440           | Rime Movement (ecumenical/"eclectic" movement)                                                           |
| BUDVAJ450           | Sakya a.k.a. Sakyapa                                                                                     |
| BUDVAJ451           | Ngor                                                                                                     |
| BUDVAJ452           | Tshar                                                                                                    |
| CHR                 | Christianity                                                                                             |
| CHR001              | Charismatic Christianity                                                                                 |
| CHR002              | conservative Christianity                                                                                |
| CHR003              | evangelical Christianity                                                                                 |
| CHR004              | liberal Christianity                                                                                     |
| CHR005              | Prosperity theology                                                                                      |
| CHR100              | ecumenical Christian movements                                                                           |
| CHR101              | World Council of Churches                                                                                |
| CHRANG              | Anglican Communion                                                                                       |
| CHRANG001           | Anglican                                                                                                 |
| CHRANG002           | Episcopalian                                                                                             |
| CHRANG011           | "conservative" Anglican                                                                                  |
| CHRANG012           | "liberal" Anglican                                                                                       |
| CHRANG013           | "high" Anglican                                                                                          |
| CHRANG014           | "low" Anglican                                                                                           |
| CHRANG015           | "Catholic" Anglican schismatic Catholics within the Anglican Communion                                   |
| CHRANG900           | Philippine Independent Church                                                                            |
| CHRANG902           | (Old Catholic Church inc. Union of Utrecht and any other Old Catholic members of the Anglican Communion) |
| CHRCTH              | Roman Catholic                                                                                           |
| CHRCTH001           | Liberation Theology                                                                                      |
| CHRCTH200 (+300)    | Roman Catholic laity                                                                                     |

Continued on next page

| Heirarchical Code   | Religion and Comments   |
|---------------------|-------------------------|
| CHRCTH201           |                         |
| CHRCTH202           |                         |
| CHRCTH203           |                         |
| CHRCTH204           |                         |
| CHRCTH205           |                         |
| CHRCTH206           |                         |
| CHRCTH207           |                         |
| CHRCTH208           |                         |
| CHRCTH209           |                         |
| CHRCTH210           |                         |
| CHRCTH211           |                         |
| CHRCTH212           |                         |
| CHRCTH213           |                         |
| CHRCTH214           |                         |
| CHRCTH400 (+500)    |                         |
| CHRCTH401           |                         |
| CHRCTH402           |                         |
| CHRCTH403           |                         |
| CHRCTH404           |                         |
| CHRCTH405           |                         |
| CHRCTH406           |                         |
| CHRCTH407           |                         |
| CHRCTH408           |                         |
| CHRCTH409           |                         |
| CHRCTH410           |                         |
| CHRCTH411           |                         |
| CHRCTH412           |                         |
| CHRCTH413           |                         |
| CHRCTH414           |                         |
| CHRCTH415           |                         |
| CHRCTH416           |                         |
| CHRCTH417           |                         |
| CHRCTH418           |                         |
| CHRCTH419           |                         |
| CHRCTH420           |                         |
| CHRCTH421           |                         |
| CHRCTH422           |                         |
| CHRCTH423           |                         |
| CHRCTH424           |                         |
| CHRCTH425           |                         |
| CHRCTH426           |                         |
| CHRCTH427           |                         |
| CHRCTH428           |                         |
| CHRCTH429           |                         |
| CHRCTH430           |                         |
| CHRCTH431           |                         |
| CHRCTH432           |                         |
| CHRCTH433           |                         |
| CHRCTH434           |                         |
| CHRCTH435           |                         |
| CHRCTH436           |                         |
| CHRCTH437           |                         |
| CHRCTH438           |                         |
| CHRCTH439           |                         |
| CHRCTH440           |                         |
| CHRCTH441           |                         |
| CHRCTH442           |                         |
| CHRCTH443           |                         |
| CHRCTH444           |                         |
| CHRCTH445           |                         |
| CHRCTH446           |                         |
| CHRCTH447           |                         |
| CHRCTH448           |                         |
| CHRCTH449           |                         |
| CHRCTH450           |                         |
| CHRCTH451           |                         |
| CHRCTH452           |                         |
| CHRCTH453           |                         |
| CHRCTH454           |                         |
| CHRCTH455           |                         |
| CHRCTH456           |                         |
| CHRCTH457           |                         |
| CHRCTH458           |                         |
| CHRCTH459           |                         |
| CHRCTH460           |                         |
| CHRCTH461           |                         |
| CHRCTH462           |                         |
| CHRCTH465           |                         |
| CHRCTH466           |                         |
| CHRCTH467           |                         |
| CHRCTH468           |                         |
| CHRCTH469           |                         |
| CHRCTH470           |                         |
| CHRCTH471           |                         |
| CHRCTH472           |                         |
| CHRCTH473           |                         |
| CHRCTH474           |                         |
| CHRCTH475           |                         |
| CHRCTH476           |                         |
| CHRCTH477           |                         |

| Heirarchical Code   | Religion and Comments   |
|---------------------|-------------------------|
| CHRCTH478           |                         |
| CHRCTH479           |                         |
| CHRCTH480           |                         |
| CHRCTH481           |                         |
| CHRCTH482           |                         |
| CHRCTH483           |                         |
| CHRCTH484           |                         |
| CHRCTH485           |                         |
| CHRCTH486           |                         |
| CHRCTH487           |                         |
| CHRCTH488           |                         |
| CHRCTH489           |                         |
| CHRCTH490           |                         |
| CHRCTH491           |                         |
| CHRCTH492           |                         |
| CHRCTH493           |                         |
| CHRCTH494           |                         |
| CHRCTH495           |                         |
| CHRCTH496           |                         |
| CHRCTH497           |                         |
| CHRCTH498           |                         |
| CHRCTH499           |                         |
| CHRCTH500           |                         |
| CHRCTH501           |                         |
| CHRCTH502           |                         |
| CHRCTH503           |                         |
| CHRCTH504           |                         |
| CHRCTH505           |                         |
| CHRCTH506           |                         |
| CHRCTH507           |                         |
| CHRCTH508           |                         |
| CHRCTH509           |                         |
| CHRCTH510           |                         |
| CHRCTH511           |                         |
| CHRCTH512           |                         |
| CHRCTH513           |                         |
| CHRCTH514           |                         |
| CHRCTH515           |                         |
| CHRCTH517           |                         |
| CHRCTH518           |                         |
| CHRCTH600           |                         |
| CHRCTH601           |                         |
| CHRCTH602           |                         |
| CHRCTH603           |                         |
| CHRCTH800           |                         |
| CHRCTH810           |                         |
| CHRCTH811           |                         |
| CHRCTH812           |                         |
| CHRCTH820           |                         |
| CHRMRN              |                         |
| CHRCTH822           |                         |
| CHRCTH823           |                         |
| CHRCTH830           |                         |
| CHRCTH831           |                         |
| CHRCTH840           |                         |
| CHRCTH841           |                         |
| CHRCTH842           |                         |
| CHRCTH850 (+800)    |                         |
| CHRCTH851           |                         |
| CHRCTH852           |                         |
| CHRCTH853           |                         |
| CHRCTH854           |                         |
| CHRCTH855           |                         |
| CHRCTH856           |                         |
| CHRCTH857           |                         |
| CHRCTH858           |                         |
| CHRCTH859           |                         |
| CHRCTH860           |                         |
| CHRCTH861           |                         |
| CHRCTH862           |                         |
| CHRCTH863           |                         |
| CHRCTH864           |                         |
| CHRCTH865           |                         |
| CHRCTH900           |                         |
| CHRCTH901           |                         |
| CHRCTH902           |                         |
| CHRCTH903           |                         |
| CHRCTH904           |                         |
| CHRCTH905           |                         |
| CHRCTH906           |                         |
| CHRCTH907           |                         |
| CHRCTH908           |                         |
| CHRCTH909           |                         |
| CHRCTH910           |                         |
| CHRDOX100           |                         |
| CHRDOX101           |                         |
| CHRDOX102           |                         |
| CHRDOX103           |                         |
| CHRDOX104           |                         |

Continued on next page

| Heirarchical Code   | Religion and Comments                                                                                |
|---------------------|------------------------------------------------------------------------------------------------------|
| CHRDOX105           | Orthodox Church of Russia                                                                            |
| CHRDOX106           | Orthodox Church of Serbia                                                                            |
| CHRDOX107           | Orthodox Church of Romania                                                                           |
| CHRDOX108           | Orthodox Church of Bulgaria                                                                          |
| CHRDOX109           | Orthodox Church of Georgia                                                                           |
| CHRDOX110           | Orthodox Church of Cyprus                                                                            |
| CHRDOX111           | Orthodox Church of Greece                                                                            |
| CHRDOX112           | Orthodox Church of Poland                                                                            |
| CHRDOX113           | Orthodox Church of Albania                                                                           |
| CHRDOX114           | Orthodox Church of the Czech lands and Slovakia                                                      |
| CHRDOX115           | Orthodox Church in America                                                                           |
| CHRDOX200           | autonomous, unrecognized, and separated Orthodox                                                     |
| CHRDOX201           | American World Patriarchs                                                                            |
| CHRDOX202           | Belarusian Autocephalous Orthodox Church                                                             |
| CHRDOX203           | Chinese Orthodox Church                                                                              |
| CHRDOX204           | Croatian Orthodox Church                                                                             |
| CHRDOX205           | Estonian Orthodox Church                                                                             |
| CHRDOX206           | Finnish Orthodox Church                                                                              |
| CHRDOX207           | Greek Old Calendars                                                                                  |
| CHRDOX208           | Japanese Orthodox Church                                                                             |
| CHRDOX209           | Latvian Orthodox Church                                                                              |
| CHRDOX210           | Macedonian Orthodox Church                                                                           |
| CHRDOX211           | Metropolitan Church of Bessarabia                                                                    |
| CHRDOX212           | Moldovan Orthodox Church                                                                             |
| CHRDOX213           | Montenegrin Orthodox Church                                                                          |
| CHRDOX214           | Old Believers                                                                                        |
| CHRDOX215           | Old Calendar Bulgarian Orthodox Church                                                               |
| CHRDOX216           | Old Calendar Romanian Orthodox Church                                                                |
| CHRDOX217           | Orthodox Church in Italy                                                                             |
| CHRDOX218           | Orthodox Church of Greece (Holy Synod in Resistance)                                                 |
| CHRDOX219           | Orthodox Ohrid Archbishopric                                                                         |
| CHRDOX220           | Patriarchal Exarchate in Western Europe                                                              |
| CHRDOX221           | Russian Orthodox Church Outside Russia                                                               |
| CHRDOX222           | Russian True Orthodox Church                                                                         |
| CHRDOX223           | Ukrainian Orthodox Church (Kyiv Patriarchate)                                                        |
| CHRDOX224           | Ukrainian Orthodox Church (Moscow Patriarchate)                                                      |
| CHRDOX300           | Oriental Orthodox Oriental Orthodox                                                                  |
| CHRDOX301           | Armenian Apostolic Church                                                                            |
| CHRCPT              | Coptic Orthodox (could also call it "CHRDOX202")                                                     |
| CHRDOX303           | Eretrian Orthodox                                                                                    |
| CHRDOX304           | Ethiopian Orthodox                                                                                   |
| CHRDOX305           | Malankara Orthodox Syrian Church (also known as Indian Orthodox)                                     |
| CHRDOX306           | Syriac Orthodox                                                                                      |
| CHRDOX400           | Assyrian Church of the East                                                                          |
| CHRDOX500           | Ancient Church of the East                                                                           |
| CHRDOX900           | schismatic Orthodox                                                                                  |
| CHRDOX910           | Old Believers - Bespovottsy                                                                          |
| CHRDOX911           | Pomortsy a.k.a. Danilovtsy                                                                           |
| CHRDOX912           | Novopomortsy a.k.a. New Pomortsy                                                                     |
| CHRDOX913           | Staropomortsy a.k.a. Old Pomortsy                                                                    |
| CHRDOX914           | Fedosevysy a.k.a. Society of Christian Old Believers of the Old Pomortsy Unmarried Confession        |
| CHRDOX915           | Fillipovtsy                                                                                          |
| CHRDOX916           | Chasovenye a.k.a. Semeyskie                                                                          |
| CHRDOX920           | Old Believers - Popovtsy                                                                             |
| CHRDOX921           | Belokrinitskaya hierarchy a.k.a. Russian Orthodox Old-Rite Church                                    |
| CHRDOX922           | Novozybkovskaya hierarchy a.k.a. Russian Old-Orthodox Church                                         |
| CHRGNO              | Gnostic Christianity                                                                                 |
| CHRGNO010           | Anthroposophy                                                                                        |
| CHRGNO020           | Foundation for Inner Peace i.e. A Course in Miracles                                                 |
| CHRGNO030           | Order of the Solar Temple                                                                            |
| CHRGNO040 (041-059) | Rosecrucianism (maybe? Esoteric knowledge Gnosticism?)                                               |
| CHRGNO041           | Ancient Mystical Order Rosca Crucis                                                                  |
| CHRGNO042           | Antiquus Ordio Roscrucianis a.k.a. Ancient Order of the Rosicrucians                                 |
| CHRGNO043           | Fraternitas Rosca Crucis                                                                             |
| CHRGNO044           | Lectorium Rosicrucianum                                                                              |
| CHRGNO045           | Rosecrucian Fellowship                                                                               |
| CHRGNO046           | Societas Rosicruciana                                                                                |
| CHRGNO060           | Summum                                                                                               |
| CHRJHW              | Bible Student Movement (mainline group: Jehovah's Witnesses)                                         |
| CHRJHW010           | Chicago Bible Students                                                                               |
| CHRJHW020           | Christian Millennial Fellowship                                                                      |
| CHRJHW030           | Dawn Bible Students                                                                                  |
| CHRJHW040           | Free Bible Students                                                                                  |
| CHRJHW041           | Berean Bible Students Church                                                                         |
| CHRJHW042           | Christian Millennial Fellowship a.k.a. Free Bible Students                                           |
| CHRJHW050           | Friends of Man a.k.a. Philanthropic Assembly of the Friends of Man, The Church of the Kingdom of God |
| CHRJHW070           | Goshen Fellowship                                                                                    |
| CHRJHW080           | Independent Bible Students                                                                           |
| CHRJHW090           | Laymen's Home Missionary Movement hostile to JW church                                               |
| CHRJHW100           | True Faith Jehovah's Witnesses Association                                                           |
| CHRLDS              | Latter Day Saints a.k.a. Mormonism                                                                   |
| CHRLDS010           | Aaronic Order numbering Aaronic Order isn't mainstream, right?                                       |
| CHRLDS020           | Church of Christ (Temple Lot)                                                                        |
| CHRLDS030           | Church of Christ with the Elijah Message                                                             |
| CHRLDS040           | Church of the Firstborn of the Fulness of Times                                                      |
| CHRLDS050           | Church of the Lamb of God                                                                            |
| CHRLDS060           | Community of Christ a.k.a. Reorganized Church of Jesus Christ of Latter Day Saints                   |
| CHRLDS061           | Restoration Branches                                                                                 |
| CHRLDS070           | Confederate Nations of Israel                                                                        |
| CHRLDS080           | Fundamentalist Church of Jesus Christ of Latter Day Saints a.k.a. FLDS                               |

| Heirarchical Code   | Religion and Comments                                                                                         |
|---------------------|---------------------------------------------------------------------------------------------------------------|
| CHRLDS090           | Latter-day Church of Christ a.k.a. Kingston Clan, Kingston Group, Davis County Cooperative, The Co-op Society |
| CHRLDS100           | Rigdonites                                                                                                    |
| CHRLDS110           | Righteous Branch of the Church of Jesus Christ of Latter-day Saints                                           |
| CHRLDS120           | The Church of Jesus Christ (Bickertonite)                                                                     |
| CHRLDS130           | The Church of Jesus Christ of Latter Day Saints (Strangite)                                                   |
| CHRLDS140           | Zion's Order                                                                                                  |
| CHRMAY001           | esoteric Christianity                                                                                         |
| CHRMAY110 (111-139) | Armstrongism (the "mainline" group is Grace Communion International)                                          |
| CHRMAY111           | Christian Churches of God                                                                                     |
| CHRMAY112           | Christian Educational Ministries                                                                              |
| CHRMAY113           | Church of God, 21st Century                                                                                   |
| CHRMAY114           | Church of God, an International Community                                                                     |
| CHRMAY115           | Church of God International (USA)                                                                             |
| CHRMAY116           | Church of God, The Eternal                                                                                    |
| CHRMAY117           | Church of God Preparing for the Kingdom of God                                                                |
| CHRMAY118           | Church of the Eternal God                                                                                     |
| CHRMAY119           | Church of the Great God                                                                                       |
| CHRMAY120           | Global Church of God (and offshoots)                                                                          |
| CHRMAY121           | Intercontinental Church of God                                                                                |
| CHRMAY122           | Living Church of God                                                                                          |
| CHRMAY123           | Philadelphia Church of God                                                                                    |
| CHRMAY124           | Restored Church of God                                                                                        |
| CHRMAY125           | Church of God Fellowship                                                                                      |
| CHRMAY126           | Church of the Great God                                                                                       |
| CHRMAY127           | Sabbath Church of God                                                                                         |
| CHRMAY128           | United Church of God                                                                                          |
| CHRMAY120           | Assemblies of Yahweh                                                                                          |
| CHRMAY130           | Bethel Ministerial Association                                                                                |
| CHRMAY140           | Christadelphian a.k.a. Thomasites                                                                             |
| CHRMAY150           | Christian Conventions a.k.a. Two-by-Twos, the Workers and Friends                                             |
| CHRMAY151           | Cooneyites                                                                                                    |
| CHRMAY160           | Christian Science a.k.a. Church of Christ, Scientist                                                          |
| CHRMAY170           | Church of the Blessed Hope                                                                                    |
| CHRMAY180           | Friends of Man                                                                                                |
| CHRMAY190           | Iglesia ni Cristo                                                                                             |
| CHRMAY200           | The Local Church a.k.a. Little Flock                                                                          |
| CHRMAY210           | Members Church of God International                                                                           |
| CHRMAY220           | Mita Congregation                                                                                             |
| CHRMAY230           | New Thought Movement inc. only the Christian, official New Thought movements                                  |
| CHRMAY231           | Church of Divine Science                                                                                      |
| CHRMAY232           | Religious Science                                                                                             |
| CHRMAY233           | Unity School of Christianity a.k.a. Unity Church                                                              |
| CHRMAY240           | Oneness Pentecostalism (maybe delete some members                                                             |
| CHRMAY241           | United Pentecostal Church International                                                                       |
| CHRMAY242           | Pentecostal Assemblies of the World                                                                           |
| CHRMAY250           | Spiritual Christianity                                                                                        |
| CHRMAY251           | Molokans                                                                                                      |
| CHRMAY252           | Duhkobors a.s.a. Doukhobors                                                                                   |
| CHRMAY253           | Khlysts                                                                                                       |
| CHRMAY254           | Skoptsy                                                                                                       |
| CHRMAY255           | Ikonobortsy                                                                                                   |
| CHRMAY260           | Swedenborgianism a.k.a. The Lord's New Church, Church of the New Jerusalem                                    |
| CHRMAY270           | The Way International American Fellowship Services                                                            |
| CHRMAY271           | Great Lakes Fellowship                                                                                        |
| CHRMAY272           | Pacific West Fellowship                                                                                       |
| CHRMAY273           | Unification Church (Moonies)                                                                                  |
| CHRMANL             | millenarian Christianity                                                                                      |
| CHRMANL010          | Branch Davidians                                                                                              |
| CHRMANL020          | The Brethren a.k.a. The Body of Christ, The Garbage Eaters                                                    |
| CHRMANL030          | Concerned Christians                                                                                          |
| CHRNM               | new Christian movements                                                                                       |
| CHRNM010            | The Body of Christ                                                                                            |
| CHRNM020            | Church of the Living Word a.k.a. The Walk                                                                     |
| CHRNM030            | The Family International                                                                                      |
| CHRNM040            | Foundation of Human Understanding                                                                             |
| CHRNM050            | International Community of Christ                                                                             |
| CHRNM060            | Shepherding Movement                                                                                          |
| CHROFF              | shootoffs of Christianity                                                                                     |
| CHROFF010           | National Spiritualist Association of Churches                                                                 |
| CHROFF020           | Spiritualism                                                                                                  |
| CHROFF030           | Unitarian-Universalism                                                                                        |
| CHROFF031           | Covenant of Unitarian Universalist Pagans                                                                     |
| CHROFF032           | Unitarianism                                                                                                  |
| CHROFF033           | Universalism                                                                                                  |
| CHROFF040           | Urantia Foundation                                                                                            |
| CHRPRO              | Protestant                                                                                                    |
| CHRPRO010           | (Protestant - generic terms/non-denominational movements)                                                     |
| CHRPRO011           | charismatic Protestantism                                                                                     |
| CHRPRO012           | cyberchurch                                                                                                   |
| CHRPRO013           | dispensationalism                                                                                             |
| CHRPRO014           | evangelical Protestantism                                                                                     |
| CHRPRO015           | pietism                                                                                                       |
| CHRPRO110 (111-139) | Adventism                                                                                                     |
| CHRPRO111           | Advent Christian Church                                                                                       |
| CHRPRO112           | Church of God (Seventh Day)                                                                                   |
| CHRPRO113           | Church of God and Saints of Christ                                                                            |
| CHRPRO114           | Church of God General Conference                                                                              |
| CHRPRO115           | Davidian Seventh-day Adventist Association                                                                    |

| Heirarchical Code   | Religion and Comments                                                                                      |
|---------------------|------------------------------------------------------------------------------------------------------------|
| CHRPRO116           | Seventh Day Adventist Reform Movement                                                                      |
| CHRPRO117           | Seventh-day Adventist Church                                                                               |
| CHRPRO118           | United Church of God                                                                                       |
| CHRPRO119           | Worldwide Church of God                                                                                    |
| CHRPRO120           | Assembly of Yahweh                                                                                         |
| CHRPRO121           | Primitive Advent Christian Church                                                                          |
| CHRPRO122           | United Seventh-Day Brethren                                                                                |
| CHRPRO123           | True and Free Adventists                                                                                   |
| CHRPRO124           | United Sabbath-Day Adventist Church                                                                        |
| CHRPRO140 (141-159) | African-initiated churches and denominations                                                               |
| CHRPRO141           | Ethiopian churches                                                                                         |
| CHRPRO142           | Zionist churches                                                                                           |
| CHRPRO143           | Messianic churches                                                                                         |
| CHRPRO144           | Apostolic churches                                                                                         |
| CHRPRO145           | Aladura Pentecostal Churches                                                                               |
| CHRPRO160 (161-179) | Anabaptism                                                                                                 |
| CHRPRO161           | Amish                                                                                                      |
| CHRPRO162           | Apostolic Christian Church (Nazarean)                                                                      |
| CHRPRO163           | Brethren in Christ                                                                                         |
| CHRPRO164           | Bruderhof                                                                                                  |
| CHRPRO165           | Church of God in Christ, Mennonite                                                                         |
| CHRPRO166           | Church of the Brethren                                                                                     |
| CHRPRO167           | Hutterites a.k.a. "New Baptists"                                                                           |
| CHRPRO168           | Mennonites                                                                                                 |
| CHRPRO169           | Old German Baptist Brethren a.k.a. Hutterian Brethren, Hutterian Society of Brothers                       |
| CHRPRO170           | Schwarzenau Brethren                                                                                       |
| CHRPRO180 (181-189) | Baptist churches                                                                                           |
| CHRPRO181           | Free and General Baptists                                                                                  |
| CHRPRO182           | Seventh Day Baptists                                                                                       |
| CHRPRO183           | Strict and Particular Baptists                                                                             |
| CHRPRO190 (191-209) | Congregationalism                                                                                          |
| CHRPRO210 (211-229) | Lutheranism                                                                                                |
| CHRPRO211           | Confessional Evangelical Lutheran Conference                                                               |
| CHRPRO212           | Evangelical Catholic Lutheran                                                                              |
| CHRPRO213           | International Lutheran Church                                                                              |
| CHRPRO214           | Lutheran World Federation                                                                                  |
| CHRPRO215           | Unaffiliated Lutheran denominations                                                                        |
| CHRPRO230 (231-239) | Methodism and Wesleyanism                                                                                  |
| CHRPRO240 (241-249) | Nazarene Church                                                                                            |
| CHRPRO250 (251-269) | Pentecostal                                                                                                |
| CHRPRO251           | Independent Pentecostalism                                                                                 |
| CHRPRO252           | Reformed/Higher Life Pentecostalism                                                                        |
| CHRPRO253           | Wesleyan/Holiness Pentecostalism                                                                           |
| CHRPRO270 (271-279) | Plymouth Brethren                                                                                          |
| CHRPRO280 (281-299) | Pre-Lutheran Protestants                                                                                   |
| CHRPRO281           | Czechoslovak Hussite Church                                                                                |
| CHRPRO282           | Moravian Church                                                                                            |
| CHRPRO283           | Unity of the Brethren                                                                                      |
| CHRPRO284           | Waldensian Evangelical Church                                                                              |
| CHRPRO300 (301-309) | Presbyterianism                                                                                            |
| CHRPRO310 (311-319) | Quakerism a.k.a. Religious Society of Friends or Society of Friends                                        |
| CHRPRO320 (321-329) | Reformed Church                                                                                            |
| CHRPRO330 (331-349) | Restoration Movement                                                                                       |
| CHRPRO331           | Churches of Christ (mainline)                                                                              |
| CHRPRO332           | Disciples of Christ a.k.a. Christian Church                                                                |
| CHRPRO333           | Independent Christian Churches/Churches of Christ                                                          |
| CHRPRO334           | International Churches of Christ                                                                           |
| CHRPRO350 (351-389) | United and uniting churches                                                                                |
| CHRPRO351           | China Christian Council                                                                                    |
| CHRPRO352           | Church of Christ in Thailand                                                                               |
| CHRPRO353           | Church of North India                                                                                      |
| CHRPRO354           | Church of Pakistan                                                                                         |
| CHRPRO355           | Church of South India                                                                                      |
| CHRPRO356           | Evangelical Church in Germany                                                                              |
| CHRPRO357           | Evangelical Free Church                                                                                    |
| CHRPRO358           | Indonesia Christian Church a.k.a. Gereja Kristen Indonesia                                                 |
| CHRPRO359           | International Council of Community Churches                                                                |
| CHRPRO360           | Protestant Church in the Netherlands                                                                       |
| CHRPRO361           | Union of Waldensian and Methodist Churches                                                                 |
| CHRPRO362           | United Church in Jamaica and the Cayman Islands                                                            |
| CHRPRO363           | United Church in Papua New Guinea and the Solomon Islands                                                  |
| CHRPRO364           | United Church of Canada                                                                                    |
| CHRPRO365           | United Church of Christ                                                                                    |
| CHRPRO366           | United Church of Christ in Japan a.k.a. Nihon Kirisuto Kyodan                                              |
| CHRPRO367           | United Church of Christ in the Philippines                                                                 |
| CHRPRO368           | United Free Church of Scotland                                                                             |
| CHRPRO370           | United Reformed Church                                                                                     |
| CHRPRO371           | Uniting Church in Australia                                                                                |
| CHRPRO900           | otherwise excluded denominations, associations, churches or movements                                      |
| CHRPRO901           | American Evangelical Christian Churches                                                                    |
| CHRPRO902           | Apostolic Christian Church of America                                                                      |
| CHRPRO903           | Association of Vineyard Churches                                                                           |
| CHRPRO904           | Born Again Movement a.k.a. Word of Life Church/Movement                                                    |
| CHRPRO905           | British New Church Movement                                                                                |
| CHRPRO906           | Brunstad Christian Church                                                                                  |
| CHRPRO907           | Calvary Chapel                                                                                             |
| CHRPRO908           | Charismatic Episcopal Church (not an offshoot of Anglicanism, but mostly uses its doctrines and materials) |
| CHRPRO909           | Christian World Liberation Front a.k.a. the Spiritual Counterfeits Project                                 |
| CHRPRO910           | Community of Jesus                                                                                         |
| CHRPRO911           | Followers of Christ Church                                                                                 |

| Heirarchical Code   | Religion and Comments                                                           |
|---------------------|---------------------------------------------------------------------------------|
| CHRPRO912           | Great Commission church movement                                                |
| CHRPRO913           | Greater Grace World Outreach                                                    |
| CHRPRO914           | Independent Fundamental Churches of America                                     |
| CHRPRO915           | Jews for Jesus                                                                  |
| CHRPRO916           | Moody Church                                                                    |
| CHRPRO918           | Most Holy Church of God in Christ Jesus                                         |
| CHRPRO919           | New Apostolic Church                                                            |
| CHRPRO920           | New Life Fellowship                                                             |
| CHRPRO921           | The Christian Community a.k.a. Christian Community Church, Christengemeinschaft |
| CHRPRO922           | True Jesus Church                                                               |
| CHRPRO923           | United Church of Christ                                                         |
| CHRRAC              | Christian groups with racial theologies                                         |
| CHRRAC010           | British Israelism a.k.a. Anglo-Israelism                                        |
| CHRRAC011           | Anglo-Saxon Federation of America                                               |
| CHRRAC020           | Christian Identity                                                              |
| CHRRAC021           | Aryan Nations Church                                                            |
| CHRRAC022           | Assembly of Christian Soldiers                                                  |
| CHRRAC023           | Christian Identity Church                                                       |
| CHRRAC024           | Church of Israel                                                                |
| CHRRAC025           | The Covenant, the Sword, and the Arm of the Lord                                |
| CHRRAD              | fundamentalist Christian                                                        |
| CHRSYN              | syncretic Christianity                                                          |
| CHRSYN010 (010-129) | Messianic Jews                                                                  |
| CHRSYN011           | Union of Messianic Jewish Congregations                                         |
| CHRSYN020           | Native American Church                                                          |
| CHRSYN030           | Sacred Name Movement a.k.a. Yahweism                                            |
| CHRSYN031           | Assemblies of the Called Out Ones of Yah"                                       |
| CHRSYN032           | Assemblies of Yahweh                                                            |
| CHRSYN033           | Yahwehs Assembly in Messiah                                                     |
| CHRSYN034           | Yahweh's Assembly in Yahshua                                                    |
| CHRSYN035           | Yahweh's Restoration Ministry                                                   |
| CHRSYN036           | Yahweh's Philadelphia Truth Congregation                                        |
| CHRSYN040           | Spiritual Baptist                                                               |
| CHRSYN050           | Uniao do Vegetal                                                                |
| CON                 | Confucianism                                                                    |
| CONSY               | Neo-Confucianism (or CON100)                                                    |
| CON200              | New Confucianism                                                                |
| HIN                 | Hinduism                                                                        |
| HIN100              | ecumenical Hindu movements                                                      |
| HIN101              | Hindu Akya Vedi                                                                 |
| HIN102              | Hindu Forum of Britain                                                          |
| HIN103              | Vishva Hindu Parish                                                             |
| HIN104              | Malaysia Hinduhudarma Mamandram                                                 |
| HIN105              | Rashtriya Swayamsevak Sang                                                      |
| HIN106              | Sanatan Sanstha                                                                 |
| HIN108              | Hindu Munnani ("of Tamilnadu")                                                  |
| HIN109              | Hindu Youth Network                                                             |
| HINAST              | Hinduism by school of astika (orthodox) philosophies                            |
| HINAST100           | Mimamsa                                                                         |
| HINAST200           | Nyaya-Vaisheshika (inc. either of the parts separately)                         |
| HINAST300           | Samkhya                                                                         |
| HINAST400 (401-699) | Vedanta                                                                         |
| HINAST410           | Advaita Vedanta                                                                 |
| HINAST420           | Vishistadvahta                                                                  |
| HINAST430           | Dvaita                                                                          |
| HINAST440           | Dvaitadvaita                                                                    |
| HINAST450           | Shuddhadvaita                                                                   |
| HINAST460           | Achintya Bhedabheda                                                             |
| HINAST470           | Purnadvaita a.k.a. Integral Advaita                                             |
| HINAST700 (701-999) | Yoga                                                                            |
| HINAST710           | Bhakti Yoga                                                                     |
| HINAST711           | Hanuman Foundation                                                              |
| HINAST720           | Hatha Yoga                                                                      |
| HINAST730           | Jnana Yoga                                                                      |
| HINAST740           | Karma Yoga                                                                      |
| HINAST750           | Riya Yoga                                                                       |
| HINAST751           | Self-Realization Fellowship                                                     |
| HINAST752           | Yogoda Satsanga Society of India                                                |
| HINAST760           | Natya Yoga                                                                      |
| HINAST770           | Purna Yoga a.k.a. Integral Yoga                                                 |
| HINAST771           | Aurobindo Ashrama                                                               |
| HINAST780           | Raja Yoga                                                                       |
| HINAST790           | named Yogic organizations                                                       |
| HINAST791           | Kripalu Yoga Retreat                                                            |
| HINAST792           | Himalayan Institute of Yoga Science and Philosophy                              |
| HINDEN              | Hinduism by denomination prioritize this categorization                         |
| HINDEN100           | Shaivism                                                                        |
| HINDEN110           | Kashmir Shaivism                                                                |
| HINDEN111           | Krana                                                                           |
| HINDEN112           | Kula                                                                            |
| HINDEN113           | Pratyabhijna                                                                    |
| HINDEN114           | Siddha Yoga                                                                     |
| HINDEN115           | Spanda                                                                          |
| HINDEN121           | Shaiva Siddhanta                                                                |
| HINDEN122           | Lingayatism                                                                     |
| HINDEN123           | Visishtadvaita                                                                  |
| HINDEN124           | Agama Hindu Dharma                                                              |
| HINDEN125           | Arsha Vidya Gurukulam                                                           |

| HINDEN126   | Religion and Comments                                                                         |
|-------------|-----------------------------------------------------------------------------------------------|
| HINDEN200   | Brahma Kumaris World Spiritual University                                                     |
| HINDEN210   | Hindu tantra                                                                                  |
| HINDEN211   | Ananda Marga                                                                                  |
| HINDEN300   | Smartism                                                                                      |
| HINDEN310   | Ramakrishna Movement (a.k.a. Vedic Movement)                                                  |
| HINDEN311   | Ramakrishna Mission (the aid work portion of the Movement)                                    |
| HINDEN312   | Ramakrishna Math                                                                              |
| HINDEN313   | Sri Sarada Math                                                                               |
| HINDEN314   | Ramakrishna Sarada Mission (Smarta) Advaita Vedanta                                           |
| HINDEN320   | Ramachandrapura Math a.k.a. Sri Sri Jagadguru Shankaracharya Mahasamstana SriSamstana Gokarna |
| HINDEN321   | Sri Ramana Ashram a.k.a. Sri Ramanasramam                                                     |
| HINDEN322   | Sharada Pitha a.k.a. Sringeri Sharma Peetham, Sringeri Mutt                                   |
| HINDEN331   | Jyotirmatha Pitha                                                                             |
| HINDEN332   | Govardhana Pitha                                                                              |
| HINDEN333   | Dwaraka Pitha                                                                                 |
| HINDEN334   | Kanchi Kamakoti Pitha                                                                         |
| HINDEN335   | Vivekananda Kendra                                                                            |
| HINDEN336   | Divine Life Society                                                                           |
| HINDEN339   | Transcendental Meditation movement a.k.a. International Meditation Society                    |
| HINDEN340   | Sivananda Yoga                                                                                |
| HINDEN341   | Divine Life Society                                                                           |
| HINDEN342   | Sathya Sai Baba                                                                               |
| HINDEN343   | Art of Living Foundation                                                                      |
| HINDEN345   | Dwaraka Pitham                                                                                |
| HINDEN346   | Govardhana Matha                                                                              |
| HINDEN347   | Jyotirmath                                                                                    |
| HINDEN348   | Warnavillatt M                                                                                |
| HINDEN350   | Kanchi Kamakoti Peetham                                                                       |
| HINDEN400   | Vaishnavism                                                                                   |
| HINDEN410   | Brahma samradaya inc. Gaudiya Vaishnavism (sole subset)                                       |
| HINDEN411   | Gaudiya Math                                                                                  |
| HINDEN412   | International Society for Krishna Consciousness a.k.a. ISKON, or Hare Krishnas                |
| HINDEN420   | Halumatha                                                                                     |
| HINDEN421   | Kaginele Kanaka Guru Peetha                                                                   |
| HINDEN422   | Mata Amritanandamayi Math                                                                     |
| HINDEN430   | Shri Vaishnava a.k.a. Sri Sampradaya                                                          |
| HINDEN431   | Andavan Ashramam                                                                              |
| HINDEN432   | Ahobila Matha                                                                                 |
| HINDEN433   | Parakala Matha                                                                                |
| HINDEN434   | Sree Narayana Dharma Paripalana Yogam                                                         |
| HINDEN435   | Sree Narayana Dharma Sangham                                                                  |
| HINDEN450   | Swaminarayan Hinduism                                                                         |
| HINDEN451   | Bochanaswani Shri Akshar Purushottam Swaminarayan Sanstha                                     |
| HINDEN452   | Swaminarayan Maninagar                                                                        |
| HINDEN453   | Swaminarayan Sampraday                                                                        |
| HINDEN451   | Astha Mathas                                                                                  |
| HINDEN452   | Kumara sampradaya                                                                             |
| HINDEN453   | Mahapuruxiya Dharma                                                                           |
| HINDEN454   | Rudra sampradaya inc. Shree Valabha Nidhi (sole subset)                                       |
| HINDEN456   | Sri Narasingha Caitanya Matha (Dvaita philosophy)                                             |
| HINDEN457   | The Ramanandi movement                                                                        |
| HINDEN458   | Vaisnava-Sahajiya                                                                             |
| HINDEN500   | Other Hindu denominations                                                                     |
| HINDEN510   | Ganapatya                                                                                     |
| HINDEN520   | Saura                                                                                         |
| HINDNAY     | Hindu groups of controversial status                                                          |
| HINDNAY010  | Ayyavazhi                                                                                     |
| HINNRM      | New Hindu Movements                                                                           |
| HINNRM010   | Arya Samaj                                                                                    |
| HINOFF      | offshoots of Hinduism                                                                         |
| HINOFF010   | Brahmoism                                                                                     |
| HINOFF011   | Sadharan Brahmo Samaj                                                                         |
| HINSYN      | syncretic Hindu movements                                                                     |
| HINSYN010   | Sant Mat and related movements                                                                |
| HINSYN011   | Radha Soami a.k.a. Radhasamo                                                                  |
| HINSYN012   | Divine Light Mission                                                                          |
| HINWLB      | wellbeing-related Hindu movements                                                             |
| HINWLB010   | Chopra Center                                                                                 |
| JAN         | Jainism                                                                                       |
| JAN100      | Digambar                                                                                      |
| JAN110      | Digambar Terapanthi                                                                           |
| JAN120      | Taran Panth                                                                                   |
| JAN200      | Svetambara                                                                                    |
| JAN210      | Baissamprada a.k.a. Bastola                                                                   |
| JAN220      | Murtipujaka                                                                                   |
| JAN230      | Sthanakvasi                                                                                   |
| JAN240      | Svetambar Terapanth                                                                           |
| JEW         | Judaism                                                                                       |
| JEW001      | (any) ecumenical Jewish organization                                                          |
| JEW010      | Conservative Judaism (should we have a Sephardic Jewish code, too?)                           |
| JEW011      | Conservadox Judaism (could also go under Orthodoxy)                                           |
| JEW012      | Masorti Judaism                                                                               |
| JEW020      | Humanistic Judaism                                                                            |
| JEW030      | Jewish Renewal                                                                                |
| JEW050      | Liberal Judaism                                                                               |
| JEW060      | Neolog Judaism                                                                                |

| Heirarchical Code   | Religion and Comments                                                                       |
|---------------------|---------------------------------------------------------------------------------------------|
| JEW070              | Orthodox Judaism                                                                            |
| JEW071              | Chief Rabbinate of Israel                                                                   |
| JEWUDX              | Haredi/Ultra-orthodox a.s.a. Chareidi, Charedi                                              |
| JEWUDX010           | Central Rabbinical Congress of the United States and Canada                                 |
| JEWHSD              | Hasidic Judaism                                                                             |
| JEWHSD010           | Chabad a.k.a. Chabad-Lubavitch                                                              |
| JEWHSD020           | Satmar                                                                                      |
| JEWUDX030           | Lithuanian/Yeshiva Haredi Judaism                                                           |
| JEW073              | Modern Orthodoxy inc. three subgroups: Edah; Orthodox Union; and Religious Zionist Movement |
| JEW074              | Union of Orthodox Rabbis                                                                    |
| JEW075              | World Agudath Israel inc. any type of Orthodox Jew                                          |
| JEW080              | Reconstructionist Judaism                                                                   |
| JEW090              | Reform/Progressive Judaism                                                                  |
| JEW800              | quasi-ethnic divisions of Judaism                                                           |
| JEW810              | Ashkenazi Judaism                                                                           |
| JEW820              | Mizrah Judaism                                                                              |
| JEW830              | Sephardic Judaism                                                                           |
| JEWNRM              | Jewish Science                                                                              |
| JEWNRM010           | offshoots of Judaism                                                                        |
| JEWOFF              | Samaritanism                                                                                |
| JEWOFF010           | Judaism with racial theories                                                                |
| JEWRAC010           | Black Hebrew Israelites                                                                     |
| JEWRAC011           | African Hebrew Israelites of Jerusalem                                                      |
| JEWRAC012           | Church of God and Saints of Christ                                                          |
| JEWRAC013           | Commandment Keepers a.k.a. Holy Church of the Living God                                    |
| JEWRAC014           | Nation of Yahweh                                                                            |
| MOSM                | Islam                                                                                       |
| MOSMAY              | Muslims of controversial status                                                             |
| MOSMAY010           | Ahmiadiyya (check this one again)                                                           |
| MOSMAY011           | Lahore Ahmiadiyya Movement                                                                  |
| MOSMAY012           | Ahmiadiyya Muslim Community                                                                 |
| MOSMAY020           | United Submitters International                                                             |
| MOSMAY030           | Zikri                                                                                       |
| MOSOFF              | shoots of Islam                                                                             |
| MOSOFF010           | Bawa Muhiayaddeen Fellowship                                                                |
| MOSOFF020           | Universal Sufism                                                                            |
| MOSOFF021           | Dances of Universal Peace                                                                   |
| MOSRAC              | racialist Islam                                                                             |
| MOSRAC100           | Black Muslim movements                                                                      |
| MOSRAC110           | American Society of Muslims (make a Black Islam section)                                    |
| MOSRAC120           | Moorish Science Temple of America                                                           |
| MOSRAC130           | Nation of Islam                                                                             |
| MOSRAC140           | Nuwaubianism                                                                                |
| MOSRAC141           | United Nuwaubian Nation of Moors                                                            |
| MOSRAC142           | Yamassee Native Americans                                                                   |
| MOSRAC150           | The Nation of Gods and Earths                                                               |
| MOSRAC160           | United Nations of Islam                                                                     |
| MOSRAD              | fundamentalist Muslim                                                                       |
| MOSSFI              | Sufi                                                                                        |
| MOSSFI010           | Mawlawi Order a.k.a. Whirling Dervishes                                                     |
| MOSSFI020           | Naqshbandi                                                                                  |
| MOSSHI              | Shia                                                                                        |
| MOSSHI100           | Twelver                                                                                     |
| MOSSHISFI           | Bektashi the Twelver Sufis                                                                  |
| MOSSHI200           | Zaidi/Zaiddiyah                                                                             |
| MOSSHI300           | Ismaili                                                                                     |
| MOSSHI310           | Alavi Bohra                                                                                 |
| MOSSHI320           | Dawoodi Bohra                                                                               |
| MOSSHI330           | Mustaali                                                                                    |
| MOSSHI331           | Hebtiahs Bohra                                                                              |
| MOSSHI332           | Abta-i-Malak                                                                                |
| MOSSHI340           | Nizari                                                                                      |
| MOSSHI350           | Sulaimani Bohra                                                                             |
| MOSDRZ              | Druze                                                                                       |
| MOSALE              | Alawi/Alewi                                                                                 |
| MOSUN               | Sunni                                                                                       |
| MOSUN010            | Hanafi school                                                                               |
| MOSUN011            | Berailvi                                                                                    |
| MOSUN012            | Deobandi                                                                                    |
| MOSUN020            | Hanbali school                                                                              |
| MOSUN030            | Maliki school                                                                               |
| MOSUN040            | Shafi'i school                                                                              |
| MOSUN040            | syncretic Islam                                                                             |
| MSSYN010            | Moorish Science Temple of America                                                           |
| SHN                 | Shinto                                                                                      |
| SHN010              | Old Shinto Schools                                                                          |
| SHN020              | folk Shinto or Ko Shinto                                                                    |
| SHN020              | Imperial Shinto                                                                             |
| SHN030              | Koshinto                                                                                    |
| SHN040              | Shrine Shinto                                                                               |
| SHNNRM              | "New Japanese Religions" (note, many groups in this section are offshoots)                  |
| SHNNRM100 (+200)    | Sect Shinto                                                                                 |
| SHNNRM110           | Fusokyo                                                                                     |
| SHNNRM120           | Izumo Oyashirokyo                                                                           |
| SHNNRM130           | Jikkokyo                                                                                    |
| SHNNRM140           | Konkokyo                                                                                    |
| SHNNRM150           | Kurozumikyo                                                                                 |

| Heirarchical Code   | Religion and Comments                                              |
|---------------------|--------------------------------------------------------------------|
| SHNNRM160           | Kyoha Shinto Rengokai                                              |
| SHNNRM170           | Misogikyo                                                          |
| SHNNRM180           | Ontakekyo                                                          |
| SHNNRM190           | Shinriyko (N.B. This is not the same as Aum Shinrikyo)             |
| SHNNRM200           | Shinto Shuseiha                                                    |
| SHNNRM210           | Shinto Taikyo                                                      |
| SHNNRM220           | Shinto Taiseikyo                                                   |
| SHNNRM230           | Tenrikyo                                                           |
| SHNNRM300 (+400)    | Shinshukyo (the second category of new religions based on Shinto)  |
| SHNNRM301           | Ananaikyo                                                          |
| SHNNRM302           | Byakko Shinkokai                                                   |
| SHNNRM303           | Chikakusan Minshukyo Kyodan                                        |
| SHNNRM304           | Chushinkai                                                         |
| SHNNRM305           | Daihizenkyo                                                        |
| SHNNRM306           | Ennokyo                                                            |
| SHNNRM307           | Hachidai Ryuo Daishizen Aishinkyodan                               |
| SHNNRM308           | Hachidai Ryuojin Hakko Seidan                                      |
| SHNNRM309           | Hachirakukai Kyodan                                                |
| SHNNRM310           | Hi no Oshie                                                        |
| SHNNRM311           | Hikari Kyokai                                                      |
| SHNNRM312           | Hizuki no Miya                                                     |
| SHNNRM313           | Honbushin                                                          |
| SHNNRM314           | Honmichi                                                           |
| SHNNRM315           | Ishinkyo                                                           |
| SHNNRM316           | Izumo Shinyu Kyokai                                                |
| SHNNRM317           | Izumokyo                                                           |
| SHNNRM318           | Jieido                                                             |
| SHNNRM319           | Jingukyo                                                           |
| SHNNRM320           | Kakushin Shukyo Nipponkyo                                          |
| SHNNRM321           | Kannagarakyo                                                       |
| SHNNRM322           | Kikueikai Kyodan                                                   |
| SHNNRM323           | Kogi Shinto                                                        |
| SHNNRM324           | Koshinto Senpokyo                                                  |
| SHNNRM325           | Koso Kotai Jingu Amatsukyo                                         |
| SHNNRM326           | Kuzuryu Taisha                                                     |
| SHNNRM327           | Kyuseishukyo                                                       |
| SHNNRM328           | Makoto no Michi                                                    |
| SHNNRM329           | Makoto no Michikyo                                                 |
| SHNNRM330           | Maruyamakyo                                                        |
| SHNNRM331           | Misogikyo Shinpa                                                   |
| SHNNRM332           | Mitamakyo                                                          |
| SHNNRM333           | Miyaji Shinsendo                                                   |
| SHNNRM334           | Nihon Jingu Honcho                                                 |
| SHNNRM335           | Nihon Seido Kyodan                                                 |
| SHNNRM336           | Nikkokyo                                                           |
| SHNNRM337           | Okanmichi                                                          |
| SHNNRM338           | Omiwakyo (Kojima)                                                  |
| SHNNRM339           | Omiwakyo (Sako)                                                    |
| SHNNRM340           | Omoto a.k.a. Oomoto                                                |
| SHNNRM341           | Omoto Hikari no Michi                                              |
| SHNNRM342           | Oyamanezu no Mikoto Shinji Kyokai                                  |
| SHNNRM343           | Perfect Liberty Kyodan a.k.a. PL Kyodan, Church of Perfect Liberty |
| SHNNRM344           | Rehi no Hikari Kyokai                                              |
| SHNNRM345           | Renmonkyo                                                          |
| SHNNRM346           | Renshindo Kyodan                                                   |
| SHNNRM347           | Samuhara Jinja                                                     |
| SHNNRM348           | Seicho no Ie                                                       |
| SHNNRM349           | Seikokyo                                                           |
| SHNNRM350           | Seimeikyo                                                          |
| SHNNRM351           | Seishin Myojokai                                                   |
| SHNNRM352           | Sekai Kyuseikyo                                                    |
| SHNNRM353           | Sekai Mahikari Bunmei Kyodan                                       |
| SHNNRM354           | Sekai Shindokyo                                                    |
| SHNNRM355           | Shidaido                                                           |
| SHNNRM356           | Shin Nihon Shukyo Dantai Rengokai                                  |
| SHNNRM357           | Shindo Tenkokyo                                                    |
| SHNNRM358           | Shinji Shumeikai                                                   |
| SHNNRM359           | Shinmei Aishinkai                                                  |
| SHNNRM360           | Shinreikai Kyodan                                                  |
| SHNNRM361           | Shinreikyo                                                         |
| SHNNRM362           | Shinri Jikko no Oshie                                              |
| SHNNRM363           | Shinsei Tengan Manaita no Kai                                      |
| SHNNRM364           | Shinto Shinkyo                                                     |
| SHNNRM365           | Shinto Shinshinkyo                                                 |
| SHNNRM366           | Shizensha                                                          |
| SHNNRM367           | Shoroku Shinto Yamatoyama                                          |
| SHNNRM368           | Shukyo Hojin Shiko Gakuen                                          |
| SHNNRM369           | Shuyodan Hoseikai                                                  |
| SHNNRM370           | Soshindo                                                           |
| SHNNRM371           | Soshindo Kyodan                                                    |
| SHNNRM372           | Subikari Koha Sekai Shindan                                        |
| SHNNRM373           | Sukui no Hikari Kyodan                                             |
| SHNNRM374           | Sukyo Mahikari                                                     |
| SHNNRM375           | Sumerakyo                                                          |
| SHNNRM376           | Taiwa Kyodan                                                       |
| SHNNRM377           | Tamamitsu Jinja                                                    |
| SHNNRM378           | Tenchikyo                                                          |
| SHNNRM379           | Tengenkyo                                                          |
| SHNNRM380           | Tenjokyo                                                           |
| SHNNRM381           | Tenjokyo Hon'in                                                    |

| Heirarchical Code   | Religion and Comments                                                                                       |
|---------------------|-------------------------------------------------------------------------------------------------------------|
| SHNNRM382           | Tenkokyo Ten'onkyo                                                                                          |
| SHNNRM383           | Tensei Shinbikay                                                                                            |
| SHNNRM384           | Tensha Tsuchimikado Shinto Honcho                                                                           |
| SHNNRM386           | Tenshin Seikyo                                                                                              |
| SHNNRM387           | Tenshindo Kyodan                                                                                            |
| SHNNRM388           | Tenshinkyo Shin'yuden Kyokai                                                                                |
| SHNNRM389           | Tensho Kotai Jingukyo                                                                                       |
| SHNNRM390           | Tenshokyo                                                                                                   |
| SHNNRM391           | Tenshukyo                                                                                                   |
| SHNNRM392           | Tokumitsukyo                                                                                                |
| SHNNRM393           | Worldmate f.k.a. Cosmomate                                                                                  |
| SHNNRM394           | Yamakage Shinto                                                                                             |
| SHNNRM395           | Yamatokyo                                                                                                   |
| SHNNRM396           | Zenrinkyo                                                                                                   |
| SHNSYN              | syncretic Shinto                                                                                            |
| SHNSYN010           | Shinbutsu shugo a.k.a. Shinbutsu konko (combines Shinto and Buddhism)                                       |
| SIK                 | Sikh mainline Sikh                                                                                          |
| SIK010              | Khalsa                                                                                                      |
| SIK011              | Nihang                                                                                                      |
| SIK020              | Sahajdhari Sikh                                                                                             |
| SIK100              | Namdhari or Kuka Sikhs new religious movements of Sikh origin                                               |
| SIKNRM010           | 3HO a.k.a. Healthy, Happy, Holy Organization                                                                |
| TAO                 | Taoist organized Taoism                                                                                     |
| TAO200              | folk Taoism                                                                                                 |
| ABR                 | (other) Abrahamic religions                                                                                 |
| ABR010              | Freemasonry Prince Hall Freemasonry Ancient Arabic Order of the Nobles of the Mystic Shrine a.k.a. Shriners |
| ABR012              | new Abrahamic movements                                                                                     |
| ABRNRM010           | Builders of the Adytum                                                                                      |
| ABRNRM020           | House of Yahweh Pilgrims of Ares                                                                            |
| ABRNRM030           | racial Abrahamic religions                                                                                  |
| ABRRAC010           | Rastafarianism                                                                                              |
| ABRRAC010           | Bobo Shanti                                                                                                 |
| ABRRAC012           | Nyahbinghi Order                                                                                            |
| ABRRAC013           | Twelve Tribes of Israel                                                                                     |
| INR                 | (other) Indian religions                                                                                    |
| INR010              | Ravidasi                                                                                                    |
| INR020              | Din-i-Ilah                                                                                                  |
| INRNRM010           | Indian NRMs                                                                                                 |
| INRNRM020           | Adidam                                                                                                      |
| INRNRM020           | Adventures in Enlightenment                                                                                 |
| INRNRM040           | Elan Vital                                                                                                  |
| INRNRM050           | Meher Baba followers                                                                                        |
| INRNRM060           | Sant Nirankari Mission                                                                                      |
| INRSYN              | Syncretic Indian religions Radha Soami Satsang Beas                                                         |
| EAR                 | (other) East Asian religions Chinese Folk Religion                                                          |
| EAR010              | Jeung San Do                                                                                                |
| EARMLN010           | EARNM                                                                                                       |
| EARNRM010           | Falun Gong                                                                                                  |
| EARSYN              | Caodaiism Chondogyo a.k.a. Chendogyo, Chendoism, Chondoism                                                  |
| EARSYN010           | I-Kuan Tao                                                                                                  |
| EARSYN020           | Kejawen/Kebatinan                                                                                           |
| EARSYN040           | African diasporic religions                                                                                 |
| ADR                 | African diasporic religions                                                                                 |
| ADR010              | Ardamble (Animism, Batuque)                                                                                 |
| ADR021              | Ketu Candomble                                                                                              |
| ADR022              | Bantu/Angola Candomble                                                                                      |
| ADR023              | Jeje Candomble                                                                                              |
| ADR030              | Kumina                                                                                                      |
| ADR040              | Macumba                                                                                                     |
| ADR050              | Mami Wata (the name refers to the deity, not the religion)                                                  |
| ADR060              | Obeah (can also be used to describe some folk practices within local Protestant denominations)              |
| ADR070              | Palo/Las Reglas de Congo                                                                                    |
| ADR080              | Winti                                                                                                       |
| ADRRSYN             | syncretic African diasporic religions                                                                       |
| ADRRSYN010          | Hoodoo                                                                                                      |
| ADRRSYN020          | Quimbanda                                                                                                   |
| ADRRSYN030          | Santera a.k.a. Lukum                                                                                        |
| ADRRSYN040          | Santo Daime                                                                                                 |
| ADRRSYN050          | Umbanda                                                                                                     |
| ADRRSYN060          | Vodou                                                                                                       |

| Heirarchical Code   | Religion and Comments                                                                           |
|---------------------|-------------------------------------------------------------------------------------------------|
| ADRSYN061           | Louisianan Voodoo                                                                               |
| ADRSYN062           | Haitian Vodou                                                                                   |
| IRR                 | (other) Iranic religions                                                                        |
| IRR010              | Ahl-e Haqq/Yarsan                                                                               |
| IRR020              | Yazidism                                                                                        |
| IRRGNO              | gnostic Iranic religion                                                                         |
| IRRGNO010           | Mandaeanism                                                                                     |
| ZRO                 | Zoroastrianism                                                                                  |
| ITR                 | indigenous tribal religions                                                                     |
| ITRCRB              | indigenous Caribbean religions                                                                  |
| ITRCRB010           | Espiritismo                                                                                     |
| ITRCRB011           | Espiritismo de Cordon                                                                           |
| ITRCRB012           | Puerto Rican Espiritismo                                                                        |
| ITRCRB013           | Table Espiritismo                                                                               |
| ITRCRB020           | Santerismo (syncretizes Espiritismo and Santera)                                                |
| ITRAM               | North American First Nations religions                                                          |
| ITRAM010            | Native American Church (Peyotism)                                                               |
| ITRWAF              | indigenous West African religions                                                               |
| ITRWAF010           | West African Vodun                                                                              |
| NRM                 | new religious movements (category of last resort)                                               |
| NRM010              | Agasha Temple of Wisdom                                                                         |
| NRM020              | Amica Temple of Radiance                                                                        |
| NRM030              | Arica School                                                                                    |
| NRM040              | Arcane School                                                                                   |
| NRM050              | Association for Research and Enlightenment                                                      |
| NRM060              | Breatharians                                                                                    |
| NRM070              | Eckankar                                                                                        |
| NRM071              | Ancient Teachings of the Masters                                                                |
| NRM080              | Esalen Institute                                                                                |
| NRM090              | Foundation for Higher Spiritual Learning                                                        |
| NRM100              | Institute of Noetic Sciences                                                                    |
| NRM110              | Kerista                                                                                         |
| NRM120              | Landmark Education                                                                              |
| NRM130              | Lucis Trust a.k.a. Lucifer Trust                                                                |
| NRM140              | Philosophical Research Society                                                                  |
| NRM150              | Rainbow Family                                                                                  |
| NRM160              | Rama computer cult                                                                              |
| NRM170              | Satanism                                                                                        |
| NRM171              | Casual/Adolescent Satanism                                                                      |
| NRM172              | LaVeyan Satanism                                                                                |
| NRM173              | Lucianism                                                                                       |
| NRM174              | Order of Nine Angels                                                                            |
| NRM175              | Our Lady of Endor Coven/Ophite Cultus Satanis                                                   |
| NRM176              | Palladists                                                                                      |
| NRM177              | Symbolic Satanism                                                                               |
| NRM178              | Temple of Set                                                                                   |
| NRM180              | Spiritual Frontiers Fellowship                                                                  |
| NRM190              | Subud                                                                                           |
| NRM200              | Universal Faithists of Kosmon                                                                   |
| NRM210              | Universal Great Brotherhood                                                                     |
| NRM220              | Universal Life Church                                                                           |
| NRM230              | White Eagle Lodge                                                                               |
| NRMGNO              | new gnostic religious movements                                                                 |
| NRMGNO100           | Fraternity of the Inner Light                                                                   |
| NRMGNO200           | Ordo Templi Orientis                                                                            |
| NRMGNO300           | Theosophy and offshoots                                                                         |
| NRMGNO310           | Aquarian Christine Church Universal                                                             |
| NRMGNO320           | Ascended Master Teachings                                                                       |
| NRMGNO321           | I AM Activity a.k.a. I AM Movement, Saint Germain Foundation                                    |
| NRMGNO322           | Summit Lighthouse inc. Church Universal and Triumphant                                          |
| NRMGNO330           | Theosophy proper (mainstream is Theosophical Society)                                           |
| NRMGNO331           | United Lodge of Theosophists                                                                    |
| NRMGNO400           | The Word Foundation                                                                             |
| NRMMLN              | Adelphi Organization                                                                            |
| NRMMLN010           | modern paganism a.k.a. Neopaganism                                                              |
| NRPAG               | ecumenical Paganism                                                                             |
| NRPAG010            | Council of Magickal Arts                                                                        |
| NRPAG020 (020-039)  | Celtic Neopaganism a.k.a. Neo-Druidism                                                          |
| NRPAG021            | Ancient Order of Druids                                                                         |
| NRPAG022            | r dNaoctin                                                                                      |
| NRPAG023            | British Druid Order                                                                             |
| NRPAG024            | Celtic Neoshamanism                                                                             |
| NRPAG025            | Celtic Reconstructionist Paganism                                                               |
| NRPAG026            | Celtic Wicca                                                                                    |
| NRPAG027            | Church of the Universal Bond                                                                    |
| NRPAG028            | Gorsedd Beird Ynys Prydain                                                                      |
| NRPAG029            | Hermetic Order of the Golden Dawn                                                               |
| NRPAG030            | Order of Bards, Ovates and Druids                                                               |
| NRPAG031            | Reformed Druids of North America                                                                |
| NRPAG032            | The Druid Order a.k.a. An Druid Uileach Braithreachas                                           |
| NRPAG030            | Baltic Neopaganism                                                                              |
| NRPAG040            | Eco-paganism                                                                                    |
| NRPAG041            | Church of Aphrodite                                                                             |
| NRPAG050            | Finnish Neopaganism                                                                             |
| NRPAG060            | German Neopaganism a.k.a. Asator, Heathenism, Heathenry, Odinism, Forn Sior, Vor Sior, Theodism |

Continued on next page

| Heirarchical Code   | Religion and Comments                                                                |
|---------------------|--------------------------------------------------------------------------------------|
| NRMPAG061           | Asatruarfelagio                                                                      |
| NRMPAG062           | Germanische Glaubens-Gemeinschaft                                                    |
| NRMPAG070           | Hellenic Neopaganism                                                                 |
| NRMPAG071           | Church of All Worlds                                                                 |
| NRMPAG072           | Feraferia                                                                            |
| NRMPAG073           | Hellenion                                                                            |
| NRMPAG074           | Supreme Council of Ethnikoi Hellenes                                                 |
| NRMPAG080           | Kemetism                                                                             |
| NRMPAG081           | Ausar Auset                                                                          |
| NRMPAG082           | Church of the Eternal Source                                                         |
| NRMPAG083           | Fellowship of Isis                                                                   |
| NRMPAG084           | Kemetic/Tameran Wicca                                                                |
| NRMPAG085           | Kemet Orthodoxy                                                                      |
| NRMPAG086           | Kemetic Reconstructionism/Revivalism                                                 |
| NRMPAG087           | Neo-Atenism                                                                          |
| NRMPAG090           | Neoshamanism                                                                         |
| NRMPAG100           | Norse paganism a.k.a. Forn Sed, Nordisk Sed, Folktro                                 |
| NRMPAG101           | Core Shamanism                                                                       |
| NRMPAG110           | Polytheistic Reconstructionism                                                       |
| NRMPAG120           | Roman Neopaganism                                                                    |
| NRMPAG130           | Slavic Neopaganism                                                                   |
| NRMPAG131           | Native Faith Association of Ukraine                                                  |
| NRMPAG132           | Native Polish Church                                                                 |
| NRMPAG133           | RUNVira                                                                              |
| NRMPAG140           | Wicca                                                                                |
| NRMPAG141           | Covenant of the Goddess                                                              |
| NRMPAG142           | Dianic Wicca                                                                         |
| NRMPAG143           | New Reformed Orthodox Order of the Golden Dawn                                       |
| NRMRAC              | new racial religious movements                                                       |
| NRMRAC010           | Ansaaru Allah Community a.k.a. Nuwaubiansm                                           |
| NRMRAC020           | Creativity                                                                           |
| NRMRAC021           | Creativity Movement                                                                  |
| NRMRAC022           | Creativity Alliance                                                                  |
| NRMRAC030           | Esoteric Nazism                                                                      |
| NRMRAC040           | Wotanism                                                                             |
| NRMSYN              | syncretic NRMs                                                                       |
| NRMSYN010           | Astara, Inc.                                                                         |
| NRMSYN020           | Lucis Trust                                                                          |
| NRMSYN021           | Arcane School                                                                        |
| NRMSYN030           | Movement of Spiritual Inner Awareness                                                |
| NRMSYN040           | Oceaniaic cargo cult                                                                 |
| NRMSYN041           | John Frum                                                                            |
| NRMSYN042           | Johnson Cult                                                                         |
| NRMSYN050           | Thelema                                                                              |
| NRMSYN060           | Vale do Amanhecer                                                                    |
| NRMUFO              | UFO cults                                                                            |
| NRMUFO010           | Aetherius Society                                                                    |
| NRMUFO020           | Chen Tao a.k.a. God's Salvation Church, God Saves the Earth Flying Saucer Foundation |
| NRMUFO030           | Heaven's Gate                                                                        |
| NRMUFO040           | Raelism                                                                              |
| NRMUFO050           | Scientology                                                                          |
| NRMUFO051           | Process Church of the Final Judgement                                                |
| NRMUFO060           | Unarius Academy of Science                                                           |
| NRMUFO070           | Universal Faithists of Kosmon                                                        |
| NRMWLN              | wellbeing-related new religious movements                                            |
| NRMWLN010           | Alcoholics Anonymous                                                                 |
| NRMWLN020           | Erhard Seminar Training                                                              |
| NRMWLN030           | Heart Consciousness Church inc. New Age Church of Being                              |
| NRMWLN040           | Human Potential Movement                                                             |
| NRMWLN041           | Silva Mind Control                                                                   |
| NRMWLN050           | Lifespring (and offshoots)                                                           |
| NRMWLN060           | Narcotics Anonymous                                                                  |
| NRMWLN070           | White Dove International                                                             |

## Chapter 9

## ISO-3166 Codes

The following table lists the ISO-3166-Alpha3 codes, which are the core of our state-level coding system. To translate between these and various other coding systems, you can use

- · CountryInfo.txt , which contains ISO-3166 numeric, alpha2 and alpha3 codes, FIPS-10 code, IMF code, COW alpha and numeric codes, http://eventdata.psu.edu/software.dir/dictionaries.html
- · Vincent Arel-Bundock's countrycode package for R includes a set of regular expressions which can be used to match country names in character strings to country codes, http://cran.r-project.org/web/packages/countrycode/index.html
- · kountry Stata module by Rafal Raciborski, http://ideas.repec.org/c/boc/bocode/s453301.html

Table 9.1: United Nations Country Codes

| Country             | UN Code   |
|---------------------|-----------|
| Afghanistan         | AFG       |
| Aland Islands       | ALA       |
| Albania             | ALB       |
| Algeria             | DZA       |
| American Samoa      | ASM       |
| Andorra             | AND       |
| Angola              | AGO       |
| Anguilla            | AIA       |
| Antigua and Barbuda | ATG       |
| Argentina           | ARG       |
| Armenia             | ARM       |
| Aruba               | ABW       |
| Australia           | AUS       |
| Austria             | AUT       |
| Azerbaijan          | AZE       |
| Bahamas             | BHS       |
| Bahrain             | BHR       |
| Bangladesh          | BGD       |
| Barbados            | BRB       |

Continued on next page

| Country                                 | UN Code   |
|-----------------------------------------|-----------|
| Belarus                                 | BLR       |
| Belgium                                 | BEL       |
| Belize                                  | BLZ       |
| Benin                                   | BEN       |
| Bermuda                                 | BMU       |
| Bhutan                                  | BTN       |
| Bolivia                                 | BOL       |
| Bosnia and Herzegovina                  | BIH       |
| Botswana                                | BWA       |
| Brazil                                  | BRA       |
| British Virgin Islands                  | VGB       |
| Brunei Darussalam                       | BRN       |
| Bulgaria                                | BGR       |
| Burkina Faso                            | BFA       |
| Burundi                                 | BDI       |
| Cambodia                                | KHM       |
| Cameroon                                | CMR       |
| Canada                                  | CAN       |
| Cape Verde                              | CPV       |
| Cayman Islands                          | CYM       |
| Central African Republic                | CAF       |
| Chad                                    | TCD       |
| Chile                                   | CHL       |
| China                                   | CHN       |
| Columbia                                | COL       |
| Comoros                                 | COM       |
| Congo, Democratic R. of the (Kinshasa)  | COD       |
| Congo, People's R. of the (Brazzaville) | COG       |
| Cook Islands                            | COK       |
| Costa Rica                              | CRI       |
| Cte d'Ivoire (Ivory Coast)              | CIV       |
| Croatia                                 | HRV       |
| Cuba                                    | CUB       |
| Cyprus                                  | CYP       |
| Czech Republic                          | CZE       |
| Denmark                                 | DNK       |
| Djibouti                                | DJI       |
| Dominica                                | DMA       |
| Dominican Republic                      | DOM       |
| East Timor (Timor-Leste)                | TMP       |
| Ecuador                                 | ECU       |
| Egypt                                   | EGY       |
| El Salvador                             | SLV       |
| Equatorial Guinea                       | GNQ       |
| Eritrea                                 | ERI       |
| Estonia                                 | EST       |

| Country                                   | UN Code   |
|-------------------------------------------|-----------|
| Ethiopia                                  | ETH       |
| Faeroe Islands                            | FRO       |
| Falkland Islands (Malvinas)               | FLK       |
| Fiji                                      | FJI       |
| Finland                                   | FIN       |
| France                                    | FRA       |
| French Guiana                             | GUF       |
| French Polynesia                          | PYF       |
| Gabon                                     | GAB       |
| Gambia                                    | GMB       |
| Georgia                                   | GEO       |
| Germany                                   | DEU       |
| Ghana                                     | GHA       |
| Gibraltar                                 | GIB       |
| Greece                                    | GRC       |
| Greenland                                 | GRL       |
| Grenada                                   | GRD       |
| Guadeloupe                                | GLP       |
| Guam                                      | GUM       |
| Guatemala                                 | GTM       |
| Guinea                                    | GIN       |
| Guinea-Bissau                             | GNB       |
| Guyana                                    | GUY       |
| Haiti                                     | HTI       |
| Holy See (Vatican City)                   | VAT       |
| Honduras                                  | HND       |
| Hong Kong Special Adm. Region of China    | HKG       |
| Hungary                                   | HUN       |
| Iceland                                   | ISL       |
| India                                     | IND       |
| Indonesia                                 | IDN       |
| Iran                                      | IRN       |
| Iraq                                      | IRQ       |
| Ireland                                   | IRL       |
| Isle of Man                               | IMY       |
| Israel                                    | ISR       |
| Italy                                     | ITA       |
| Jamaica                                   | JAM       |
| Japan                                     | JPN       |
| Jordan                                    | JOR       |
| Kazakhstan                                | KAZ       |
| Kenya                                     | KEN       |
| Kiribati                                  | KIR       |
| Korea, Democratic People's R. (Pyongyang) | PRK       |
| Korea, Republic of (Seoul)                | KOR       |
| Kuwait                                    | KWT       |

| Country                            | UN Code   |
|------------------------------------|-----------|
| Kyrgyzstan                         | KGZ       |
| Laos                               | LAO       |
| Latvia                             | LVA       |
| Lebanon                            | LBN       |
| Lesotho                            | LSO       |
| Liberia                            | LBR       |
| Libya                              | LBY       |
| Liechtenstein                      | LIE       |
| Lithuania                          | LTU       |
| Luxembourg                         | LUX       |
| Macao Special Adm. Region of China | MAC       |
| Macedonia                          | MKD       |
| Madagascar                         | MDG       |
| Malawi                             | MWI       |
| Malaysia                           | MYS       |
| Maldives                           | MDV       |
| Mali                               | MLI       |
| Malta                              | MLT       |
| Marshall Islands                   | MHL       |
| Martinique                         | MTQ       |
| Mauritania                         | MRT       |
| Mauritius                          | MUS       |
| Mayotte                            | MYT       |
| Mexico                             | MEX       |
| Micronesia                         | FSM       |
| Moldova                            | MDA       |
| Monaco                             | MCO       |
| Mongolia                           | MNG       |
| Montenegro                         | MTN       |
| Montserrat                         | MSR       |
| Morocco                            | MAR       |
| Mozambique                         | MOZ       |
| Myanmar                            | MMR       |
| Namibia                            | NAM       |
| Nauru                              | NRU       |
| Nepal                              | NPL       |
| Netherlands                        | NLD       |
| Netherlands Antilles               | ANT       |
| New Caledonia                      | NCL       |
| New Zealand                        | NZL       |
| Nicaragua                          | NIC       |
| Niger                              | NER       |
| Nigeria                            | NGA       |
| Niue                               | NIU       |
| Norfolk Island                     | NFK       |
| Northern Mariana Islands           | MNP       |

| Country                          | UN Code   |
|----------------------------------|-----------|
| Norway                           | NOR       |
| Occupied Palestinian Territory   | PSE       |
| Oman                             | OMN       |
| Pakistan                         | PAK       |
| Palau                            | PLW       |
| Panama                           | PAN       |
| Papua New Guinea                 | PNG       |
| Paraguay                         | PRY       |
| Peru                             | PER       |
| Philippines                      | PHL       |
| Pitcairn                         | PCN       |
| Poland                           | POL       |
| Portugal                         | PRT       |
| Puerto Rico                      | PRI       |
| Qatar                            | QAT       |
| Runion                           | REU       |
| Romania                          | ROM       |
| Russia                           | RUS       |
| Rwanda                           | RWA       |
| Saint Helena                     | SHN       |
| Saint Kitts-Nevis                | KNA       |
| Saint Lucia                      | LCA       |
| Saint Pierre and Miquelon        | SPM       |
| Saint Vincent and the Grenadines | VCT       |
| Samoa                            | WSM       |
| San Marino                       | SMR       |
| Sao Tome and Principe            | STP       |
| Saudi Arabia                     | SAU       |
| Senegal                          | SEN       |
| Serbia                           | SRB       |
| Seychelles                       | SYC       |
| Sierra Leone                     | SLE       |
| Singapore                        | SGP       |
| Slovakia                         | SVK       |
| Slovenia                         | SVN       |
| Solomon Islands                  | SLB       |
| Somalia                          | SOM       |
| South Africa                     | ZAF       |
| Spain                            | ESP       |
| Sri Lanka                        | LKA       |
| Sudan                            | SDN       |
| Suriname                         | SUR       |
| Svalbard and Jan Mayen Islands   | SJM       |
| Swaziland                        | SWZ       |
| Sweden                           | SWE       |
| Switzerland                      | CHE       |

Continued on next page

| Country                      | UN Code   |
|------------------------------|-----------|
| Syria                        | SYR       |
| Tajikistan                   | TJK       |
| Tanzania                     | TZA       |
| Thailand                     | THA       |
| Togo                         | TGO       |
| Tokelau                      | TKL       |
| Tonga                        | TON       |
| Trinidad and Tobago          | TTO       |
| Tunisia                      | TUN       |
| Turkey                       | TUR       |
| Turkmenistan                 | TKM       |
| Turks and Caicos Islands     | TCA       |
| Tuvalu                       | TUV       |
| Uganda                       | UGA       |
| Ukraine                      | UKR       |
| United Arab Emirates         | ARE       |
| United Kingdom               | GBR       |
| United States                | USA       |
| United States Virgin Islands | VIR       |
| Uruguay                      | URY       |
| Uzbekistan                   | UZB       |
| Vanuatu                      | VUT       |
| Venezuela                    | VEN       |
| Viet Nam                     | VNM       |
| Wallis and Futuna Islands    | WLF       |
| Western Sahara               | ESH       |
| Yemen                        | YEM       |
| Zambia                       | ZMB       |
| Zimbabwe                     | ZWE       |

## Chapter 10

## Regional Dictionaries

At various points in the Keds project we developed dictionaries focused on specific geographical regions. We currently have three main regional dictionaries-the Middle East, the Balkans, and West Africa. We have also developed a unique, separate dictionary for Turkey. In addition to following the same format and rules, these dictionaries also have a chunk of entries-actors and corresponding codes-in common. Most countries and major international actors, for instance, are found in all of the dictionaries. They differ from each other only in that each contains additional entries that are relevant only for the issues and the countries in that particular region; the difference occurs because we develop separate dictionaries-verbs and actors-for each region using leads relevant for that region. However, because the creation of dictionaries is systematic and consistent process, the regional dictionaries can be compared and merged at any time to build comprehensive main dictionaries. (We do merge our dictionaries periodically; hence, the initial dictionaries we use in our regional dictionary developments were at one time created from the merging of a number of smaller and more regional dictionaries.) The following sub-sections describe and list the special actor codes-those that have special suffixes attached to make them more specific than the generic codes, as well as the special group identity codes-that are found in respective dictionaries.

A major difference that sets the actors dictionary for Turkey apart from our other actor dictionaries is its incorporation of idiosyncratic codes-typically dealing with generic agents who are assumed to be Turkish (see Table 10.4)-that make the dictionary unsuitable for use in coding other countries. Its merging with other dictionaries would therefore require the elimination of certain entries. See the sub-section on Turkey for more details.

Note that the actual dictionaries are much longer than what are listed in this codebook; what is listed here are the codes that one encounters in our dictionaries or in the output at the analysis stage, and not all the entries that correspond to each code. In many cases, domestic actors are also simply assigned generic codes (such as country or identity code plus the domestic role code) when they are entered in the dictionaries. It is only when one wants to make a distinction between different actors with the same generic code-for instance, between two or more coalition partners in a government-that special codes are created. It is important to continually update this codebook and include new special codes, if any are created; otherwise, the analysis stage would be complicated since what the different codes refer to will not have been documented (except in the dictionary itself).

## 10.0.4 Ethnicity and Religion

In the regional dictionaries, some identity groups are specifically identified as residing in particular countries, generally explicitly (e.g. "Canadian Tamils" or "Christians in Baghdad"). In such cases,

religious/ethnic identity codes are added to the country codes (e.g. HRVSER for ethnic Serbs living in Croatia).

These identity codes can in some cases also be composed of six letters, instead of three. For example, the code for the Druze is MOSDRZ , and when an actor is specifically known to be a Lebanese Druze, then the code becomes LBNMOSDRZ . In instances where the actor is known to be religious in nature (such as a reference to priest, monk, abbot, etc.) but the religious affiliation is not identified the Generic Religious ( REL ) code should be used. Lists of such identity codes exist in Tables 10.1 and 10.2.

The original religious codes were adapted from HURIDOCS but are very general and give uneven levels of specificity. We eventually intend to replace this with the far more detailed religious group classification in CAMEORCS (Chapter but the older system will be found in many of the regional dictionaries.

By convention, ethnicity always precedes religion in a CAMEO code.

Table 10.1: Main Ethnic Group Codes in KEDS Regional Dictionaries

| Ethnic Group   | Code   |
|----------------|--------|
| Albanian       | ABN    |
| Arab           | ARB    |
| Bedouin        | BED    |
| Chakma         | CKM    |
| Croat          | CRO    |
| Gypsy          | GYP    |
| Hausa          | HAU    |
| Hutu           | HUT    |
| Ibo            | IBO    |
| Ijaws          | IJW    |
| Krahn          | KRH    |
| Kurd           | KUR    |
| Mandingoe      | MAN    |
| Ogoni          | OGO    |
| Palestinian    | PAL    |
| Serb           | SER    |
| Slav           | SLV    |
| Sinhalese      | SNL    |
| Tamil          | TAM    |
| Tuareg         | TRG    |
| Turk           | TRK    |
| Tutsi          | TUT    |
| Uighur         | UIG    |
| Yoruba         | YRB    |

Table 10.2: Main Religious Group Codes (from HURIDOCS)

| Religious Group             | Code   |
|-----------------------------|--------|
| Unspecified Religious       | REL    |
| Agnostic/Atheist            | ATH    |
| Alewi                       | MOSALE |
| Animist/Pagan               | PAG    |
| Bahai                       | BAH    |
| Buddhist                    | BUD    |
| Christian                   | CHR    |
| Catholic                    | CHRCTH |
| Coptic                      | CHRCPT |
| Jehovah's Witnesses         | CHRJHW |
| Latter Day Saints           | CHRLDS |
| Maronite                    | CHRMRN |
| Orthodox Christian          | CHRDOX |
| Protestant                  | CHRPRO |
| Confucian                   | CON    |
| Hindu                       | HIN    |
| Jain                        | JAN    |
| Jew                         | JEW    |
| Hasidic                     | JEWHSD |
| Orthodox/Ultra-Orthodox Jew | JEWUDX |
| Muslim                      | MOS    |
| Druze                       | MOSDRZ |
| Shi'a                       | MOSSHI |
| Sikh                        | SIK    |
| Sufi                        | MOSSFI |
| Sunni                       | MOSSUN |
| Taoist                      | TAO    |
| Zoroastrian                 | ZRO    |

## 10.0.5 The Middle East

The Arab-Israeli conflict, particularly the conflict between Israel and the Palestinians, has been our primary focus in coding the Middle East. Hence, our dictionary is most developed with respect to domestic political actors in Israel and Palestine. As part of a separate project, we have also extensively coded Algeria, and the actors dictionary from that project has been merged with our Levant dictionary. We started coding Turkey using this more general Middle East dictionary. Due to the presence of idiosyncratic codes, we have not merged the actors dictionary we developed for Turkey back into this dictionary; this could still be done, however, selectively.

Table 10.3 shows a list of the actors with special codes in the Middle East dictionary. Note that because of the dynamic nature of the domestic positions of many of these actors (for instance, an opposition party yesterday but a government coalition party today), many are date-restricted, so that the domestic generic codes that specify their positions can vary depending on the date of each news report. 'd.r.' refers to 'date-restricted'; for the exact dates refer to the dictionary itself.

While the code PSE (UN code) refers to the Occupied Palestinian Territories of the West Bank and the Gaza Strip, PAL refers to Palestinians as an identity group. Therefore, Palestinian government and other state actors are coded as PSEGOV , PSECOP , etc. depending on their respective roles. The Palestinian Liberation Organization (PLO), however, is coded as PALPLO as it represents the Palestinian people in general; because of its unusual status, the PLO could not be assigned one of the generic domestic role codes. The organizations underneath the PLO are each assigned codes based on their spheres of influence. Hence, Yasser Arafat and Fatah are date restricted as PALPLO before the Oslo Accords of 1993-which marked the establishment of the Palestinian Authority-and as PSEGOV thereafter. (Fatah itself is in fact further specified as PSEGOVFTA .)

Table 10.3: Special Actor Codes for the Middle East

| Actor/Domestic Region                             | Code                        |
|---------------------------------------------------|-----------------------------|
| Abu Nidal Organization                            | PALREBANO                   |
| Al Aqsa Martyrs Brigade                           | PSEREBAAM                   |
| Al Qaeda                                          | IMGMOSALQ                   |
| Amal Militia                                      | LBNREBAML                   |
| Arab (ethnic group)                               | ARB                         |
| Arab Israeli                                      | ISRARB                      |
| Armed Islamic Group (GIA)                         | DZAREBGIA                   |
| Baath Party                                       | ARBTH                       |
| Baghdad                                           | IRQBAG                      |
| Democratic Front for the Lib. of Palestine (DFLP) | PSEREBDFL                   |
| Democratic National Rally                         | DZAGOVRND                   |
| Ennahda Movement                                  | DZAOPPENN                   |
| Fatah                                             | PALPLO, PSEGOVFTA (d.r.)    |
| Gaza Strip                                        | PSEGZS                      |
| Hamas                                             | PSEREBHMS, PSEGOVHMS (d.r.) |
| Hezbollah                                         | LBNREBHEZ                   |
| Islamic Action Front                              | JOROPPIAF                   |
| Islamic Salvation Army                            | DZAREBFIS                   |
| Islamic Salvation Front                           | DZAOPPFIS                   |
| Israeli Communist Party                           | ISROPPCMN                   |
| Israeli Labor Party                               | ISROVLBA, ISROPPLBA (d.r.)  |
| Israeli Settlers                                  | ISRSET                      |
| Kurd (ethnic group)                               | KUR (TURKUR, IRQKUR, etc.)  |
| Kurdish Democratic Party (KDP)                    | IRQKURKDP                   |
| Likud Party                                       | ISRGOVLKD, ISROPLKD (d.r.)  |
| Meretz Party                                      | ISROVMRZ, ISROPPMRZ (d.r.)  |
| Movement of the Society for Peace                 | DZAGOVMSP, DZAOPPMSP (d.r.) |
| Muslim Brotherhood                                | EGYREMBBR                   |
| National Liberation Front (FLN)                   | DZAGOVFLN, DZAOPPFLN (d.r.) |
| Occupied Palestinian Territories                  | PSE                         |
| Palestine Liberation Front                        | PALREBPLF                   |
| Palestine Liberation Organization                 | PALPLO                      |
| Palestinian                                       | PAL                         |
| Palestinian Islamic Jihad                         | PSEREBISJ                   |
| People's Mujahedeen                               | IRNREBPMD                   |
| Polisario Guerrillas                              | MARREBPLS                   |
| People's Front for the Lib. of Palestine (PFLP)   | PSEREBPFL                   |
| Salafist Group                                    | DZAREBGSP                   |
| Shas Party                                        | ISRGOVSHA, ISROPPSHA (d.r.) |
| South Lebanon Army                                | LBNREBASL                   |
| Taliban                                           | AFGGOVTAL, AFGREBTAL (d.r.) |
| West Bank                                         | PSEWSB                      |

## 10.0.6 Turkey

As mentioned above, CAMEO's actor dictionary for Turkey is unique in that it includes idiosyncratic codes which require that it not be used without certain modifications when coding other countries. The reason is that it gives vaguely identified actors codes that identify them as actors associated specifically with Turkey (even if the information is not explicit in the new leads). For example, "rebels" who are not further specified are coded as TURREB and "soldiers" similarly unspecified are coded as TURMIL. We were able to do that since Turkey was the only country included in that project and it was the only country listed in our search string for news leads; we could reasonably assume that the insufficiently specified actors we come across would in most cases be associated with Turkey.

Table 10.4 shows a list of these unique codes which are present only in our special actors dictionary for Turkey. Note that because TABARI gives precedence to longer patterns over less specified, shorter entries, when news leads further specify the identity of these actors and they are entered into the dictionary as such, these idiosyncratic codes are trumped. For example, "Kurdish rebels" are coded as KURREB and "Iraqi police" is coded as IRQCOP.

In the context of Turkey, "village guards" refer to Kurdish locals in Southeast Turkey recruited by the military to fight Kurdish guerrillas, mainly the rebels associated with the Kurdistan Workers' Party (PKK)-coded TURREBPKK. Hence, although they are not officially associated with the Turkish state and the Turkish military, village guards are coded as TURMIL; this is how we would code stateponsored paramilitaries.

We also deviate from the normal CAMEO protocol in coding what are called "State Security Courts" (Devlet Guvenlik Mahkemeleri, DGMs) in Turkey. Until June 1999, these courts included military judges and were commonly regarded as being controlled by the Turkish Armed Forces. Therefore, although court systems are typically coded as JUD (or TURJUD in case of Turkey), we code "State Security Courts" as TURMIL for dates prior to 990618. These courts were finally abolished in May 2004.

Unlike Table 10.4, Table 10.5 presents a list of special actor codes which could be integrated into other dictionaries. Again, note that what is listed here are the codes that one encounters in the dictionary or in the output at the analysis stage, and not all the entries that correspond to each code. The key for coding Turkey is to get the date-restrictions right; with the exception of post-2003, the multi-party period in Turkey has been marked by short-lived coalition governments and frequent elections. Furthermore, the banning of political parties and their rebirths with slightly changed names have been commonplace in Turkey, thereby requiring date-restrictions to null-code closed parties.

Also, while Turkey is a unitary state and there was little legal basis for giving geographic regions or cities their own special codes, it proved essential to introduce certain regions and cities as different actors in order to facilitate the coding of domestic contentious politics events.

Table 10.4: Ambiguous Actors and Idiosyncratic Codes for Turkey

| Ambiguous Actor           | Code   |
|---------------------------|--------|
| "Activist(s)"             | TUROPP |
| "Guerilla(s)"             | TURREB |
| "Gunman/Gunmen"           | TURREB |
| "Police"                  | TURCOP |
| "Prisoner(s)"             | TUROPP |
| "Protester(s)"            | TUROPP |
| "Rebel(s)"                | TURREB |
| "Soldier(s)"              | TURMIL |
| "State Security Court(s)" | TURMIL |
| "Village Guard(s)"        | TURMIL |

Table 10.5: Special Actor Codes for Turkey

| Actor/Domestic Region                     | Code                        |
|-------------------------------------------|-----------------------------|
| Ankara                                    | TURANK                      |
| Democratic People's Party (DEHAP/HADEP) 1 | TUROPPHDP                   |
| Democratic Left Party (DSP)               | TUROPPDSP, TURGOVDSP (d.r.) |
| Democratic Society Party (DTP)            | TUROPPDTP                   |
| Dev-SOL                                   | TURREBDSL                   |
| Istanbul                                  | TURIST                      |
| Izmir                                     | TURIZM                      |
| Justice and Development Party (AK Party)  | TUROPPAKP, TURGOVAKP (d.r.) |
| Kurdistan Workers' Party (PKK)            | TURREBPKK                   |
| Kurds in Turkey                           | TURKUR                      |
| Motherland Party (ANAP)                   | TUROPPANP, TURGOVANP (d.r.) |
| National Action Party (MHP)               | TUROPPMHP, TURGOVMHP (d.r.) |
| Republican People's Party (CHP)           | TUROPPCHP, TURGOVCHP (d.r.) |
| Southeast Turkey                          | TURSOE                      |
| True Path Party (DYP)                     | TUROPDYP, TURGOVDYP (d.r.)  |
| Virtue Party (Fazilet)                    | TUROPPFAZ                   |
| Welfare Party (Refah)                     | TUROPPREP, TURGOVREP (d.r.) |

$^{1}$DEHAP and HADEP are in fact different political parties, both representing the Kurdish opposition in Turkey. DEHAP, which later joined DTP in 2005, is seen as the continuation of HADEP, which was banned in 2003.

## 10.0.7 West Africa

In addition to coding West Africa in general with CAMEO, we also coded Liberia and Nigeria for separate projects. Therefore, the West Africa dictionary is most developed for these two countries. Also, because of the level of political decentralization and the importance of intra-state ethnic interactions in these countries, numerous special region codes have been developed particularly to represent the federal states within Nigeria and the counties of Liberia. The domestic region codes for Nigeria are listed in Table 10.6 and those for Liberia are listed in Table 10.7. Note that some of these regions, such as the Niger Delta region in Nigeria, do not constitute legal boundaries but still represent politically important divisions within their respective countries.

Other region-specific special codes are listed in Table 10.8. Ethnic groups are coded as six character codes if the exact location of the actors is not specified: the Ogoni people of Nigeria, for example, are coded as NGAOGO as long as the news report does not associate the actor with a more specific region within the country, but as NGAABUGO if the specific actor in question is identified as being from Abuja. The same applies to other ethnic groups and other regions. Note that most of the political and militant groups and organizations in this region are not being assigned special codes; this is not because they are not important enough to warrant special codes, but because the first six characters are typically the codes for the country and the region/the ethnic group ( NGAHAU , NGAAGU , LBROGO , etc.), and the last three characters are then generally used to specify the roles of the actors. For example, the O'odua Peoples Congress (a Yoruba rebel group) in Nigeria is assigned the code NGAYRBREB -Nigeria, Yoruba, rebel group-which is not a special code (i.e., any Yoruba rebel group would be assigned the same code). Also, note that only a few of the special political organization codes are date-restricted; this reflects the current state of the dictionary, but this could, and should, change as coding continues and the roles of these actors change.

Table 10.6: Nigerian States/Regions with Special Codes

| Region             | Full Code   |
|--------------------|-------------|
| Abuja              | NGAABU      |
| Abia               | NGAABI      |
| Adamawa            | NGAADA      |
| Akwa Ibom          | NGAAKI      |
| Anambra            | NGAANB      |
| Bauchi             | NGABAU      |
| Bayelsa            | NGABAY      |
| Benue              | NGABNU      |
| Biafra             | NGABIA      |
| Borno              | NGABOR      |
| Cross River        | NGACRR      |
| Delta              | NGADEL      |
| Ebonyi             | NGAEBO      |
| Edo                | NGAEDO      |
| Ekiti              | NGAEKI      |
| Enugu              | NGAENU      |
| Gombe              | NGAGOM      |
| Imo                | NGAIMO      |
| Jigawa             | NGAJIG      |
| Kaduna             | NGAKAD      |
| Kano               | NGAKAN      |
| Katsina            | NGAKAT      |
| Kebbi              | NGAKEB      |
| Kogi               | NGAKOG      |
| Kwara              | NGAKWA      |
| Lagos              | NGALAG      |
| Nassarawa          | NGANAS      |
| Niger              | NGANGR      |
| Niger Delta Region | NGANDR      |
| North Nigeria      | NGANNG      |
| Ogun               | NGAOGU      |
| Ondo               | NGAOND      |
| Osun               | NGAOSU      |
| Oyo                | NGAOYO      |
| Plateu State       | NGAPLA      |
| Rivers             | NGARIV      |
| Sokoto             | NGASOK      |
| Taraba             | NGATAR      |
| Yobe               | NGAYOB      |
| Zamfara            | NGAZAM      |

Table 10.7: Liberian Counties/Regions with Special Codes

| Region           | Full Code   |
|------------------|-------------|
| Bomi             | LBRBOM      |
| Bong             | LBRBON      |
| Grand Cape Mount | LBRCAP      |
| Grand Gedeh      | LBRGGC      |
| Grand Bassa      | LBRGBA      |
| Grand Kru        | LBRKRU      |
| Lofa             | LBRLOF      |
| Margibi          | LBRMRG      |
| Maryland         | LBRMRY      |
| Montserrat       | LBRMNT      |
| Nimba            | LBRNIM      |
| Rivercess        | LBRRVC      |
| Sino             | LBRSIN      |

Table 10.8: West African Actors with Special Codes

| Actor                                               | Code                        |
|-----------------------------------------------------|-----------------------------|
| All Liberia Coalition Party                         | LBROPPALC                   |
| All Nigeria People's Party                          | NGAOPPANP                   |
| Armed Forces of Liberia                             | LBRREBAFL, LBRMIL (d.r.)    |
| Campaign for Democracy                              | NGAOPPCFD                   |
| Hausa (ethnic group)                                | NGAHAU                      |
| Ibo, a.k.a. Igbo (ethnic group)                     | NGAIBO                      |
| Ijaws (ethnic group)                                | NGAIJW                      |
| Independent NPFL                                    | LBRREBINP                   |
| Kamajor militia                                     | SLEREBKAM                   |
| Krahn (ethnic group)                                | LBRKRH                      |
| Liberia Action Party                                | LBROPPLAP, LBRGOVLAP (d.r.) |
| Liberia Peace Council                               | LBRREBLPC                   |
| Liberians United for Reconciliation and Democracy   | LBRREBLUR                   |
| Mandingoe (ethnic group)                            | LBRMAN                      |
| Movement for the Advancement of Democracy (MAD)     | NGAREBMAD                   |
| National Democratic Party of Liberia                | LBROPPNDP, LBRGOVNDP (d.r.) |
| National Democratic Coalition of Nigeria (NADECO)   | NGAOPPNDC                   |
| National Patriotic Front of Liberia (NPFL)          | LBRREBNPF, LBRGOVNPF (d.r.) |
| National Union for the Total Ind. of Angola (UNITA) | AGOREBUNI                   |
| New Deal Movement                                   | LBROPPNDM                   |
| Ogoni (ethnic group)                                | NGAOGO                      |
| Revolutionary United Front                          | SLEREBRUF                   |
| Tiv (ethnic group)                                  | NGATIV                      |
| United Liberation Front for Democracy               | LBRREBULM                   |
| United People's Party                               | LBROPPUPP, LBRGOVUPP (d.r.) |
| Yoruba (ethnic group)                               | NGAYRB                      |

## 10.0.8 The Balkans

Our focus in coding the Balkans has primarily been on the conflict and conflict resolution events during the first half of 1990s. The Balkans actors dictionary is, therefore, most developed with respect to ethnic and territorial divisions (as opposed to specific political parties or organizations).

## The Former Yugoslavia

The state of the Socialist Federal Republic of Yugoslavia disintegrated by 1992 with the breaking away of its constituents republics, eventually forming the states of Slovenia (UN code SVN ), Croatia (HRV ), the Former Yugoslavia Republic of Macedonia (MKD ), Bosnia and Herzegovina (BIH ), and Serbia and Montenegro (SCG ).

Bosnia and Herzegovina, created with the Dayton Agreement of 14 December 1995 which brought three years of civil war to an end, has a federal structure that consists of two republics: the Bosniak/Croat Federation of Bosnia and Herzegovina (BIHBHF ) and the Bosnian Serb Republics Srpska (BIHSRP ). Generic role codes (such as GOV , MIL , OPP , etc.) for actors associated with BIHBHF and BIHSRP become the last three characters of the actor codes. In order to differentiate between the states/republics and the people as ethnic groups, Bosnian Muslims are coded as BIHMOS (not BIHBHF ), Bosnian Croats as BIHCRO , and Bosnian Serbs as BIHSER (not BIHSRP ). More generally, CRO and SER refer to Croat and Serb ethnic groups. If an actor with a given ethnicity is associated with either one of the federal units specifically, the ethnicity code can be attached to the six-character unit code (e.g. BIHBHFSER ). Generic role codes (such as GOV , MIL , OPP , REB ) can also be used as the last three-character.

After the fellow constituent republics of Slovenia, Croatia, Macedonia, and Bosnia-Herzegovina declared independence in 1991, Serbia and Montenegro-the remaining federal states of the Socialist Federal Republic of Yugoslavia-formed the Federal Republic of Yugoslavia (then UN code FRY ). On February 4, 2003, however, a new constitution was accepted, abdicating this self-proclaimed successor to the Socialist Federal Republic of Yugoslavia and replacing it with a loose federation called Serbia and Montenegro (UN code, hence the CAMEO code, becomes SCG ). The new federation consisted of the two states of Serbia (SCGSRB ) and Montenegro (SCGMTN ), as well as the two autonomous provinces of Kosovo (SCGSKV ) and Vojvodina (SCGVVD ). With Montenegro's unilater declaration of independence on 3 June 2006, followed by Serbia's declaration on 5 June 2006, SCG also ceased to exist and gave way to two independent states: MTN and SRB (with SRBKSV and SRBVVD as autonomous provinces).

Note that the state of Serbia has a code that is different from that of the ethnic group of Serbs, who might or might not be living in Serbia. When an actor is associated with the ethnic group of Serbs and its country of origin is not specified, the actor is assigned the code SER ; if the Serb in question is associated with a certain location such as Bosnia-Bosnian Serb-then the code becomes BIHSER (not BIHSRB or BIHSCG ). The same rule applies to the other ethnic groups.

A more comprehensive list of major actor groups in the region and their respective codes can be found in Table 10.9. Note that actors with generic codes are not listed; the point here is to document the different codes-not to list all actor entries, which would mean replicating the whole dictionary-that exist in the dictionaries so that codes which show up in the output can be easily identified during analysis. Actors listed in the last group are derivations of different ethnic groups living in different countries. This list is not exhaustive; those listed here are meant as examples of how state/country codes and codes for ethnic groups living in those countries are merged to create special group codes.

Table 10.9: Special Actor Codes for the Balkans

| Actor                                 | Full Code   |
|---------------------------------------|-------------|
| Albania                               | ALB         |
| Croatia                               | HRV         |
| Former Yugoslav Republic of Macedonia | MKD         |
| Bosnia and Hercegovina                | BIH         |
| Federation of Bosnia-Hercegovina      | BIHBHF      |
| Republika Srpska                      | BIHSRP      |
| Serbia                                | SRB         |
| Montenegro                            | MTN         |
| Kosovo                                | SRBKSV      |
| Vojvodina                             | SRBVVD      |
| Albanian                              | ABN         |
| Croat                                 | CRO         |
| Serb                                  | SER         |
| Turk                                  | TRK         |
| Gypsy                                 | GYP         |
| Slav                                  | SLV         |
| Bosnian Croat                         | BIHCRO      |
| Croatian Serb                         | HRVSER      |
| Kosovar Albanian                      | SRBKSVABN   |
| Bosnian Muslim                        | BIHMOS      |
| Bosnian Serb                          | BIHSER      |
| Kosovar Serb                          | SRBKSVSRB   |

## Chapter 11

## SUPPLEMENTS

## 11.1 Actor Coding Cheatsheet

Sarah Stacey, KEDS Project Coder

2010

- · Underscore, underscore, underscore.
- · Never use "a", "an", or "the" in the beginning of an entry in the actors dictionary.
- · When entering just a name (e.g. KOFI ANNAN ) without a job title (specifying organization, ethnicity, etc.), always date restricti The entry U.N. SECRETARY GENERAL KOFI ANNAN does not require a date restriction, because you can assume he is [IGOUNO] by definition.
- · Do not use only first or last names such as ROBERTS or ABDULLAH that can be confused with other actors. In 99% of cases, you need to use the full name and/or attach the title (for example, SAUDI KING ABDULLAH ).
- · Remember to include all information given.

GOVERNMENT OWNED BUSINESS [~GOVBUS] MILITARY COURT [~MILJUD] STATE OWNED NEWS [~GOVMED]

- · Use your judgment on when one identity supersedes another.

AMERICAN\_U.N.\_OBSERVER [IGOUNO] FIJIAN\_PEACEKEEPING\_SOLDIER [IGOPKO].

- · Dont confuse ethnicity with territory. Be careful with [PAL] vs. [PSE], and [ARB] vs. [MEA].
- · Dont be fooled when the title is not in the code.

ARAB\_ALLY\_JORDAN [JOR] ARAB\_CAPITALS [MEA]

- · Any political party should be opposition or government with date restrictions. This also goes for Labor and Communist parties (not [ LAB ] OR [ CMN ] ).
- · When entering nouns and adjectives, only add an "s" if necessary. For example, never add "negotiations", but rather "negotiation" so that you do not have add it again when the singular form comes up.
- · Never inject your own bias.

EGYPTIAN\_FUNDAMENTALIST\_GROUP [EGYMOSTRAD] ;*** 7/17/01

This entry assumes that all fundamentalist groups in Egypt are also Islamic.

## 11.2 Ten (or Eleven) Commandments on Verb Phrases

- 1. There are some verbs that innately express intent such as plan, prepare, promise, pledge, vow etc. But most all others, like "provide" or "sign", need a WILL , IS TO etc. in order to code in the [030]'s to differentiate betweens events that have taken place and those that have not. Instead of individualized codes for each, use brackets to cover your bases:

```
ACCEPT
  - { WOULD | IS_TO_ | WILL } *  MEDIATION [039]
  (Express intent to mediate)
```

- 2. When there is a formal agreement between two actors that describes a specific form of cooperation, always be as specific as possible, instead of always coding it as [057:057] .

SIGN

- % * MILITARY ACCORD [062:062]

It is most accurate to say the parties are engaging in military cooperation.

- 3. Only use the code [139] (give ultimatum) if cannot you specify another type of threat:

ATTEND

- WILL\_NOT\_* TALKS UNLESS +

In this case, use [134] (Threaten to halt negotiations) instead of [139] .

- 4. Codes such as RECEIVE → + * SUPPORT FROM $ produce miscodes because they can be so many different ones: [070] , [051] , etc. Add (the minimally needed number of) words to give such vague phrases context.

RECEIV

- + * FINANCIAL SUPPORT FROM $ [071]

- 5. Especially with problematic verbs like strike, always be sure to include necessary contextual information.

SAID WOULD * AGAINST +

This could be [138] (threaten with military force) or [133] (threaten with political dissent). Instead, make the code

SAID WORKERS WOULD GO\_ON\_* AGAINST + [133]

to erase the ambiguity.

- 6. Restoring diplomatic relations is coded as [050:050] (Engage in diplomatic cooperation) , but establishing diplomatic relations is coded as [054:054] (Grant diplomatic recognition) .
- 7. When Peacekeepers arrive and are received, it is a reciprocal event: [074:0861] .
- 8. Use [175] (Use tactics of violent repression) , instead of [173] (Impose curfew) , for events where protesters/demonstrators/etc. are arrested, as we are capturing the fact that the government is using repression to restore order.
- 9. Adding nouns as verbs gets messy. Try to avoid this at all cost.
- 10. When in doubt, consult the CAMEO or TABARI codebook!
- 11. Whenever sensible, file a verb pattern under the first verb to appear in the pattern. The first verb in a pattern is almost always the conjugated verb.

ATTACK

- - PROMIS TO\_*

PROMIS

- - * TO\_ATTACK

These two verb patterns are essentially identical-there's no reason to have both. However, the second is preferable, because it will be read first in a sentence. Hence, if we have the sentence " Gondor promised to attack Mordor with tanks ", and the verb pattern

PROMIS

- - * TANKS [1384]

the second verb pattern will overwrite the third, but the first pattern will not.

## Bibliography

- [1] edward E. azar. The conflict and peace data bank (COPDAB) project. Journal of Conflict Resolution , 24:143-152, 1980.
- [2] edward E. azar. The codebook of the conflict and peace data bank (COPDAB) . Center for International Development, University of Maryland, College Park, MD, 1982.
- [3] edward E. azar and Thomas Sloan. Dimensions of Interaction . University Center for International Studies, University of Pittsburgh, Pittsburgh, 1975.
- [4] doug Bond, brad Bennett, and william Vogele. data development and interaction events analysis using keds/panda: an interim report. paper presented at the International Studies Association, washington, 1994.
- [5] doug Bond, joe Bond, churl Oh, J. craig Jenkins, and charles L. taylor. integrated data for events analysis (IDEA): an event typology for automated events data development. Journal of Peace Research , 40(6):733-745, 2003.
- [6] john L. daves and chad K. mcDaniel. the global event-data system. in richard L. merritt, robert g. muncaster, and dina a. zinnes, editors, International Event-Data Developments: DDIR Phase II . university of michigan press, ann arbor, 1993.
- [7] russell j leng. behavioral correlates of War, 1816-1975. (ICPSR 8606) . Inter-University Consortium for political and social research, ann arbor, 1987.
- [8] charles a. mclelland. world-event-interaction-survey: a research project on the theory and measurement of international interaction and transaction. university of southern california, march 1967.
- [9] charles a. mclelland. world event/interaction survey codebook (ICPSR 5211) . InterUniversity Consortium for political and social research, ann arbor, 1976.
- [10] charles a. mclelland. let the user beware. international studies quarterly , 27(2):169-177, 1983.
- [11] sean p. o'brien. crisis early warning and decision support: contemporary approaches and thoughts on future research. international studies review , 12(1):87-104, 2010.
- [12] bruce m. russett, j. david singer, and melvin small. national political units in the twentieth century: a standardized list. american political science review , 62(3):932-951, 1968.
- [13] philip a. schrodt. twenty years of the kansas event data system project. The political methodologist , 14(1):2-8, 2006.

- [14] Philip A. Schrodt and Deborah J. Gerner. Validity assessment of a machine-coded event data set for the Middle East, 1982-1992. American Journal of Political Science , 38:825-854, 1994.
- [15] Philip A. Schrodt, Deborah J. Gerner, and O ¨ mur Yilmaz. Conflict and mediation event observations (CAMEO): An event data framework for a post Cold War world. In Jacob Bercovitch and Scott Gartner, editors, International Conflict Mediation: New Approaches and Findings . Routledge, New York, 2009.
- [16] Rodney G. Tomlinson. World event/interaction survey (WEIS) coding manual. Mimeo, Department of Political Science, United States Naval Academy, Annapolis, MD, 1993.