# CoSwID - Code Switching Identification

This repository is related to the article "CoSwID, a Code Switching Identification Method Suitable for Under-Ressourced Languages", presented at the [SIGUL Workshop](https://sigul-2022.ilc.cnr.it/) ([LREC2022](https://lrec2022.lrec-conf.org/en/)) by [Laurent Kevers](https://orcid.org/0000-0001-5058-6706) (University of Corsica).

## Purpose

CoSwID allows language identification at word level, with the objective of identifying monolingual segments in multilingual text. It can therefore be used for - but is not limited to - code switching detection.

The proposed code and data are designed to take into account nine European languages (eight official languages of the European Union - English, Italian, German, French, Portuguese, Spanish, Dutch and Romanian - plus one under-resourced regional language of France: Corsican).

Given the low resource requirements for each language supported by the system, it is relatively easy to integrate under-resourced languages. It is therefore possible to adapt the system to other languages with some modifications and a minimal set of additional linguistic resources.

CoSwID is based on the use of a language identification module. We choosed *ldig*, but it is possible to adapt the system to use any other module that would return results compatible with the processing performed.

## Requirements

- This repository content (code and data)
- *ldig* : available in the [ldig-python3](https://github.com/lkevers/ldig-python3) GitHub repository
- *dicServer* : available in the [dicServer]() GitHub repository

## Installation

__Requirements__:

	git clone https://github.com/lkevers/ldig-python3.git
	git clone https://github.com/lkevers/dicServer.git
	git clone https://github.com/lkevers/coswid.git

__Settings__:

[dicServer] : If you don't use the provided resources, specify the location of each language resource.

> In dicServer/dicServer.py, see load_dictionaries()

[LDIG] : Build language models including all the languages your are interested in (or use an existing model). Example to generate 'FILTER2' model :

	cd data_lgID_learn
	unzip filter2.zip
	cat filter2/LEARN_data_filter2_* >>filter2/LEARN_data_filter2_ALL.txt
	mkdir ../models/filter2
	cd ../../ldig-python3
	python3 ldig.py -m ../CoSwID/models/filter2 -x maxsubst/maxsubst --init ../CoSwID/data_lgID_learn/filter2/LEARN_data_filter2_ALL.txt
	python3 ldig.py -m ../CoSwID/models/filter2 --learn ../CoSwID/data_lgID_learn/filter2/LEARN_data_filter2_ALL.txt -e 0.5
	python3 ldig.py -m ../CoSwID/models/filter2 --shrink

>	Please note that the second call to ldig takes a long time (potentially several hours, depending on your hardware and the volume of data).

To test the model (each line is processed as a document, the result is displayed on the standard output):

	python3 ldig.py -m ../CoSwID/models/filter2 ../CoSwID/test.txt

[CoSwID] : Check and specify if necessary the location of LDIG (ldig-pyhton3)

>	In CoSwID/src/coswid.py, search for 'INSTALL(1)'

[CoSwID] : Specify the location of the language model(s)

>	In CoSwID/src/coswid.py, search for 'INSTALL(2)' : 'modelList' variable

[CoSwID] : Specify the languages covered by each model

>	In CoSwID/src/coswid.py, search for 'INSTALL(2)' : 'lgList' variable

[CoSwID] : Check and specify the short/long language codes used, and their conversion tables

>	In CoSwID/src/coswid.py, search for 'INSTALL(2)' : 'toShortLgCode' and 'toLongLgCode' variables

[CoSwID] : Check the alphabet specification

>	In CoSwID/src/coswid.py, search for 'INSTALL(2)' : 'alphabet' variable

[CoSwID] : Check the default values

>	In CoSwID/src/coswid.py, search for 'INSTALL(3)'


## Running

First launch dicServer, as explained in the [dicServer's documentation](https://github.com/lkevers/dicServer) (specify <WORKING_DIRECTORY>):

	python3 dicServer.py <WORKING_DIRECTORY>

Execute CoSwID on a text file, with selected parameter values. Eg. from the CoSwID main directory, on the provided test.txt :

	python3 src/coswid.py -m FILTER2 -t test.txt -c 2 -f 0 -g 0.1 -v dico

>	The result is automatically stored into an output file 'test.txt.out'.
	Information about the processing is displayed on the standard output. It can be redirected to a file using the '>' operator.

Alternatively, you can directly provide some text after the ''-t' parameter. Please use the double quotes (") to delimit the text to process:

	python3 coswid.py -m FILTER2 -t "Voici un texte à analyser in order to predict the languages" -c 2 -f 0 -g 0.1 -v dico

The result is available in a file called "default.out" located in the current directory.


## Results

The results are provided in an output file. Each line contain two columns : the original word and the assigned language code. Par exemple :

	Voici   fra
	un      fra
	texte   fra
	à       fra
	analyser        fra
	in      eng
	order   eng
	to      eng
	predict eng
	the     eng
	languages       eng


## Performances

During our tests and evaluations, CoSwID achieved an overall accuracy between 87.29% and 97.97%.
It was compared to other available systems. For further details, please refer to the [SIGUL/LREC paper](http://www.lrec-conf.org/proceedings/lrec2022/workshops/SIGUL/pdf/2022.sigul-1.15.pdf).


## Citation

__How to cite__:

Kevers Laurent, CoSwID, a Code Switching Identification Method Suitable for Under-Ressourced Languages, In: *Proceedings of 1st Annual Meeting of the ELRA/ISCA Special Interest Group on Under-Resourced Languages (SIGUL 2022)*, 24-25 June 2022, Marseille, France.
[SIGUL/LREC paper](http://www.lrec-conf.org/proceedings/lrec2022/workshops/SIGUL/pdf/2022.sigul-1.15.pdf)

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
