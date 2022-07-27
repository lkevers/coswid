# CoSwID - Code Switching Identification : Test & Gold standard Data.

These data are related to the article "CoSwID, a Code Switching Identification Method Suitable for Under-Ressourced Languages", presented at the [SIGUL Workshop](https://sigul-2022.ilc.cnr.it/) ([LREC2022](https://lrec2022.lrec-conf.org/en/)) by [Laurent Kevers](https://orcid.org/0000-0001-5058-6706) (University of Corsica).

## The UDHR data

Original UDHR data is in the Public Domain. They are available on the NLTK version (”udhr2” corpus) available on https://www.nltk.org/nltk_data/.

These modified corpora are released under the CC BY-NC-SA 4.0 license (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)

UDHR-paragraph contains 16,095 tokens spread over 531 paragraphs, a switch of language occurring at each paragraph break.

UDHR-sentence contains 16,097 tokens divided into 621 sentences, the language being changed for each new sentence.

UDHR-word contains 18,417 tokens and 2,598 language switching sequences.

These files contain **synthetic**, artificially built, language switching data.

It includes the following files :
1. Raw text files:
  * eval_UDHR_paragraph.txt
  * eval_UDHR_sentence.txt
  * eval_UDHR_word.txt
2. Annotated gold standard text files
  * gold_UDHR_paragraph.txt
  * gold_UDHR_sentence.txt
  * gold_UDHR_word.txt

## The BDLC data

This data includes 328 ethnotexts (transcripts of oral interviews conducted in Corsican, in which passages in French may occur) coming from the BDLC Project (Corsican Language Database, https://bdlc.univ-corse.fr). The full collection of BDLC ethnotexts can be consulted on https://bdlc.univ-corse.fr/concord/#?lang=en.

It contains 79,421 tokens, 74,569 (93.89%) are in Corsican, 4,042 (5.09%) in French – spread over 959 segments – and 810 (1.02%) without an attributed language (abbreviations, proper nouns or speech turn markers when they were identified).

These data are **authentic** examples of language switching (code switching).

It is released under the CC BY-NC-SA 4.0 license (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en).

It includes the following files :
1. Raw text files:
  * eval_BDLC_ethno.txt
2. Annotated gold standard text files
  * gold_BDLC_ethno.txt
