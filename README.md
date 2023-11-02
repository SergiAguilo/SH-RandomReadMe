# SH-Worker
This program: 
    1. Gets a random README from github and send it to a Bioinformatics Classifier Model. 
    2. Gets the classification result ("Bioinformatics" or "Not Bioinformatics") from an API. 
    3. If the classification result is "Bioinformatics", it will extract metadata from the README using [SOMEF](https://somef.readthedocs.io/en/latest/). 
    4. [Maybe] Sends the metadata to a GitHub repository of the Research Software Ecosystem. 
