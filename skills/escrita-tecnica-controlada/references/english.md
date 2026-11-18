# Controlled technical English and the bilingual pipeline

Read this file when the output language is English or when the user wants Portuguese and English versions. Sections 1 to 4 govern English text. Sections 5 to 8 govern the pt-BR ↔ en workflow; their Portuguese examples stay in Portuguese because Portuguese is the object of the rules.

## Table of Contents

1. [Scope](#1-scope)
2. [The ten rules in English](#2-the-ten-rules-in-english)
3. [Limits by level](#3-limits-by-level)
4. [Word choice: avoid → use](#4-word-choice-avoid--use)
5. [Bilingual pipeline](#5-bilingual-pipeline)
6. [Proposition table](#6-proposition-table)
7. [What to copy and what to adapt](#7-what-to-copy-and-what-to-adapt)
8. [Calques to avoid](#8-calques-to-avoid)

## 1. Scope

These rules follow the principles of ASD-STE100 (Simplified Technical English). They do not reproduce its dictionary, and they do not certify compliance. For certified aerospace documentation, use the official standard.

The same three levels apply: `strict` (procedures, error messages, tool descriptions, prompts), `descriptive` (reports, documentation, PR descriptions), `light` (internal messages).

## 2. The ten rules in English

1. **Put the conclusion first.** The first sentence gives the result, the decision, or the main instruction.
2. **Name the actor.** Use the active voice. Use the passive voice only in descriptive text when the actor is unknown or not important. If the source does not name the actor, write `[to confirm: who does X?]`.
3. **One idea in each sentence, one verb form for each text type.** Instructions use the imperative ("Open the file"). Descriptions use the simple present ("The service validates the token"). Reports of events use the simple past. Use a simple tense when it gives the same meaning as a compound tense. Keep the progressive form when it marks an action in progress ("The worker is processing the queue"): the simple present would change it into a habit. Do not use an "-ing" clause to connect two ideas: "Run X, generating Y" does not say if Y is the purpose or the result. Write "Run X to generate Y" or "Run X. X generates Y" if the source confirms one. If not, keep the sentence and add `[to confirm: purpose or result?]`.
4. **Keep modality and uncertainty.** "Must" is an obligation. "Can" is a capability. "May" is a permission. For probability, use "possibly", "probably", or a number. "Should" has three readings: a recommendation, an estimate, or an obligation. Keep the actor and the action in each case. For "The process should stop in 5 minutes": if the source confirms an estimate, write "The estimated time is 5 minutes". If the source confirms a requirement, write "The process must stop in 5 minutes". If the source confirms a recommendation, write "We recommend that the process stops in 5 minutes". Add "or less" only if the source confirms that 5 minutes is a maximum. Without confirmation, keep the sentence and add `[to confirm: recommendation, estimate, or obligation?]`. A hedge in the source stays a hedge.
5. **Separate facts, inferences, and gaps.** Give the source of each fact (`file:line`, command, log line). Mark each inference. Say what you did not verify.
6. **Use numbers and names, not adjectives.** "Fast", "several", "soon", and "robust" give no data. Write the value, the unit, and the date.
7. **Use the full verb and the simple word.** "Perform a validation of" becomes "validate". "Utilize" becomes "use". Do not use phrasal verbs with a non-literal meaning ("spin up", "tear down", "kick off"): write "start", "delete", "start".
8. **Use one term for one concept.** Do not rotate synonyms ("check / verify / validate"). Use one word in one part of speech. Expand an acronym at first use.
9. **Keep the syntax flat.** Put the condition and the safety warning first. Use no more than three nouns in a noun cluster ("database connection timeout" is the limit). Do not omit articles or verbs ("Service restarted, error persists" becomes "The service was restarted. The error persists." Name the actor only if the source names it.). Do not use semicolons. Use a vertical list for three or more steps or conditions.
10. **Remove noise.** Delete text that carries no fact, condition, or instruction: "Great question!", "I hope this helps", "It is worth noting that", "Let's dive in", "In today's fast-paced world".

## 3. Limits by level

| Limit | `strict` | `descriptive` | `light` |
|---|---|---|---|
| Words in a sentence | 20 | 25 | 30 |
| Subordinate clauses in a sentence | 1 | 2 | free |
| Sentences in a paragraph | 6 | 6 | 6 recommended |
| Nouns in a cluster | 3 | 3 | free |

Formats: decimal point (`1.5 GB`), thousands comma (`10,000`), ISO 8601 dates (`2026-03-14`), 24-hour time with the time zone (`14:30 BRT`), a space between number and unit (`300 ms`).

## 4. Word choice: avoid → use

| Avoid | Use |
|---|---|
| utilize, leverage, make use of | use |
| perform / carry out / conduct + noun | the verb |
| in order to | to |
| due to the fact that | because |
| prior to, subsequent to | before, after |
| in the event that | if |
| at this point in time | now |
| a number of, several, various | the number |
| and/or | "and", "or", or "A, B, or both" |
| once (for time) | when, after |
| since (for cause) | because |
| as (for cause) | because |
| while (for contrast) | but, although |
| should | "Must" for a confirmed obligation. "The estimate is" for a confirmed estimate. "We recommend" for a confirmed recommendation. If not confirmed, keep "should" and add `[to confirm: …]`. |
| may | "Possibly" for a possibility. "Is permitted to" for a permission. "Can" only for a capability. If the source does not show the reading, keep "may" and add `[to confirm: …]`. |
| ensure, make sure | "Keep" when the system holds a condition ("the controller keeps the valve closed"). "Verify" or "confirm" when someone checks one time. The obligation in the source stays the same. |
| impact, affect | increase, decrease, stop (give the direction) |
| robust, seamless, powerful, cutting-edge, comprehensive, world-class | the measured property |
| crucial, critical, essential, key (as emphasis) | "mandatory" if it is a requirement, or delete |
| delve, dive into, explore, unpack, navigate, landscape, journey, tapestry | the direct verb, or delete |
| it is worth noting that, it is important to note that, please note that | delete |
| simply, basically, really, very | delete when the word adds only emphasis |
| not just X, but Y | If X and Y are facts, write the two: "The service is a cache and a proxy". If no one stated X, write Y. |

Keep "only", "just", and "actually" when they restrict or correct something: a quantity ("only one test failed"), a person ("just administrators can approve"), an action, or a condition. To delete the word would change the fact.

Each row of this table applies when the word has the meaning shown and the replacement keeps the same statement. If the replacement changes who acts, what is permitted, or what is restricted, keep the original word.

---

## 5. Bilingual pipeline

The order is mandatory. Normalizing the two languages in parallel from the raw original makes the versions diverge.

1. **Rewrite the source text** with the rules of its own language. The source is the language of the input. The controlled text is the reference.
2. **Translate the controlled text**, never the raw original.
3. **Apply the rules of the target language** only where they do not change the meaning.

Never round-trip (PT → EN → PT). Each translation reintroduces ambiguity.

**The other language works as a linter.** If the Portuguese rule requires information that the English did not give (the actor of a passive, whether "should" is an obligation), the problem is ambiguity in the source. Go back to step 1.

- Do not choose the plausible answer. The answer comes from the author or from the text.
- With no answer, mark both languages: `[to confirm: …]` and `[a confirmar: …]`. List the questions under "A confirmar".

Example:

- Source: "The report should be sent after validation."
- Questions: who sends? who validates what? is "should" a recommendation, an estimate, or an obligation?
- No answer: "`[to confirm: who?]` should `[to confirm: recommendation, estimate, or obligation?]` send the report after `[to confirm: who validates what?]`." / "`[a confirmar: quem?]` deveria `[a confirmar: recomendação, estimativa ou obrigação?]` enviar o relatório depois que `[a confirmar: quem valida o quê?]`." The modality stays open in both languages.
- With the answer: "The scheduler must send the report after the gateway validates the token." / "O agendador deve enviar o relatório depois que o gateway valida o token."

## 6. Proposition table

To check equivalence, do not ask "do the versions say the same thing?". Extract from each version, independently, a table with the columns of the fidelity check in `SKILL.md`: actor, action, object, condition, modality, polarity, quantifier and value with unit, tense and aspect, source of the evidence. Add a column with the relation of each statement to the previous one (cause, consequence, alternative, order). Compare cell by cell.

The check fails when:

- a cell exists in one version and is missing in the other, or the values differ
- the relation between two statements changes from one version to the other
- a glossary term receives two translations

A difference in the count of steps, conditions, or values calls for a review of the correspondence and does not fail the check alone: one language can join in one sentence what the other says in two.

The word count does not need to match. Portuguese uses 10 to 15 % more words, and for that reason the Portuguese limits are 25 and 30, against 20 and 25 in English.

Deliver the two versions with the same structure of headings and lists, in the same order, to allow side-by-side review.

## 7. What to copy and what to adapt

**Copy unchanged:** identifiers, variable and field names, flags, parameters, log lines, error codes, file names, and paths.

**Interface label:** use the real label of the product in the target language. Do not invent a translation. If the product has no translation, keep the original label.

**Format that changes:**

| Item | pt-BR | en |
|---|---|---|
| Decimal | `1,5 GB` | `1.5 GB` |
| Thousands | `10.000` | `10,000` |
| Date | `2026-08-02` | `2026-08-02` |
| Time | `14h30` | `14:30` |
| Currency | `R$ 1.200,50` | `BRL 1,200.50` |

A value inside code, YAML, JSON, or a log keeps the format of the program in both languages.

## 8. Calques to avoid

Columns: English source, the Portuguese calque not to write, the Portuguese to write. The Portuguese cells stay in Portuguese because they are the object of the rule.

| Inglês | Não escreva | Escreva |
|---|---|---|
| Make sure the service is running | Faça certeza de que… | Confirme que o serviço está ativo |
| Once the job finishes | Uma vez que o job termina | Quando o job termina |
| Run X, generating Y | Execute X, gerando Y | "Execute X para gerar Y" se a fonte confirma finalidade. "Execute X. X gera Y" se confirma consequência. |
| You should restart | Você deveria reiniciar | "Reinicie" se a fonte confirma obrigação. "Recomendamos reiniciar" se confirma recomendação. Sem confirmação, marcador. |
| database connection timeout | timeout de conexão de banco de dados | tempo limite da conexão com o banco de dados |
| This allows you to… | Isso permite que você… | "Com isso, você pode…" quando é permissão. "Com isso, você consegue…" quando é capacidade. |
| It is recommended that | É recomendado que | Recomendamos (diga quem recomenda) |
| actually | atualmente | na verdade |
| eventually | eventualmente | por fim |
| assume | assumir | supor |
| support (a format) | suportar | aceitar |
| requirement | requerimento | requisito |
| library | livraria | biblioteca |
| push (git) | empurrar | enviar |
| issue | questão | problema / item |

In the opposite direction (pt-BR → en): "eventualmente" is "sometimes", not "eventually". "Atualmente" is "currently", not "actually". "Pretender" is "intend", not "pretend". The hidden subject of Portuguese needs a subject in English: if the original does not say who, use `[to confirm: who?]`.
