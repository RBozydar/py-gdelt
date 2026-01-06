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
