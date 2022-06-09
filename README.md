# CoSwID - Code Switching Identification

This repository is related to the article "CoSwID, a Code Switching Identification Method Suitable for Under-Ressourced Languages", presented at the [SIGUL Workshop](https://sigul-2022.ilc.cnr.it/) ([LREC2022](https://lrec2022.lrec-conf.org/en/)) by [Laurent Kevers](https://orcid.org/0000-0001-5058-6706) (University of Corsica).

## Purpose

CoSwID allows language identification at word level, with the objective of identifying monolingual segments in multilingual text. It can therefore be used for - but is not limited to - code switching detection.

The proposed code and data are designed to take into account nine European languages (eight official languages of the European Union - English, Italian, German, French, Portuguese, Spanish, Dutch and Romanian - plus one under-resourced regional language of France: Corsican).

It is possible to adapt the system to other languages with some modifications and a minimal set of additional linguistic resources.

CoSwID is based on the use of a language identification module. We choosed *ldig*, but it is possible to adapt the system to use any other module that would return results compatible with the processing performed.

## Requirements

- This repository content (code and data)
- *ldig* : available in the [ldig-python3](https://github.com/lkevers/ldig-python3) GitHub repository
- *dicServer* : available in the [dicServer]() GitHub repository

## Installation



## Running


## Performances

During our tests and evaluations, CoSwID achieved an overall accuracy between 87.29% and 97.97%.
It was compared to other available systems. For further details, please refer to the SIGUL paper.


## Citation

__How to cite (to appear)__:

Kevers Laurent, CoSwID, a Code Switching Identification Method Suitable for Under-Ressourced Languages, In: *Proceedings of 1st Annual Meeting of the ELRA/ISCA Special Interest Group on Under-Resourced Languages (SIGUL 2022)*, 24-25 June 2022, Marseille, France.

This work was carried out thanks to CPER funding: "Un outil linguistique au service de la Corse et des Corses: la Banque de Données Langue Corse (BDLC)".

You can visit the [Corsican Language Database](https://bdlc.univ-corse.fr/bdlc/corse.php) page and the [NLP for Corsican](https://bdlc.univ-corse.fr/tal/) page for any further information.

## Licenses

- CoSWID Code : [CeCILL_V2.1](http://www.cecill.info/licences/Licence_CeCILL_V2.1-fr.html)
- Test & Gold Data - UDHR : [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)
- Test & Gold Data - BDLC : [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)
- Language Identification Data - Corsican - Wikipedia : [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)
- Language Identification Data - Corsican - A Sacra Bìbbia (the Bible) : [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
- Language Identification Data - Corsican - A Piazzetta : [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
- Language Identification Data - Other Languages - Tatoeba : [CC BY 2.0 FR](https://creativecommons.org/licenses/by/2.0/fr/deed.en).


<!--
It will be updated with source code as soon as possible.
In the meantime, most of the data is already available under the "Data" folder.
-->
