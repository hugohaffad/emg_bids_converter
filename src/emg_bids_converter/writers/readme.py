"""Writer for the README.md file."""

from pathlib import Path


_TEMPLATE_BODY = """
# GENERAL INFORMATION
 
## Dataset title:
 
## DOI:
 
## Contact email:
 
<Here is a list of suggested items to help you enrich your documentation if necessary.
Some may not be applicable, depending on the dataset’s discipline or context of production.>
 
<***Remove or add any section if applicable***>
 
# METHODOLOGICAL INFORMATION 
 
## Environmental/experimental conditions: 
 
## Description of sources and methods used to collect and generate data:
<If applicable, describe standards, calibration information, facility instruments, etc. > 
 
## Methods for processing the data: 
< If applicable, describe how submitted data were processed and include details that may be important for data reuse or replication. Add comments to explain each step taken.
For example, include data cleaning and analysis methods; code and/or algorithms, de-identification procedures for sensitive data human subjects or endangered species data.> 
 
## Quality -assurance procedures performed on the data: 
 
## Other contextual information:
<Any information that you consider important for the evaluation of the dataset’s quality and reuse thereof: for example, information about the software required to interpret the data. 
If applicable and not covered above, include full name and version of software, and any necessary packages or libraries needed to read and interpret the data, *e.g.* to run scripts.>

# DATA-SPECIFIC INFORMATION FOR: [FILENAME]
 
<Repeat this section for each folder or file, as appropriate. Recurring items may also be explained in a common initial section.>
 
<For tabular data, provide a data dictionary/code book containing the following information:>
## Variable/Column List:
For each variable or column name, provide: 

	-- full “human readable” name of the variable, 
	-- description of the variable, 
	-- unit of measurement if applicable, 
	-- decimal separator *i.e.* comma or point if applicable
	-- allowed values : list of values or range, or domain
	-- format if applicable, e.g. date>
 
## Missing data codes: 
<Define codes or symbols used to indicate missing data.>
 
## Additional information: 
<Any relevant information you consider useful to better understand the file>
"""


def write_readme(dataset_root: Path, dataset_name: str) -> Path:
    """Write README.md file."""
    readme_path = Path(dataset_root) / "README.md"
    readme_path.write_text(f"# {dataset_name}\n{_TEMPLATE_BODY}", encoding="utf-8")
    return readme_path
