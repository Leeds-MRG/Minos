# Compiling Page 

Github page is writting using sphinx and the readthedocs.io theme. To recompile the website locally make any changes in the source docsrc folder to desired rst and md files.

When changes are made run in /docsrc

>make github

Should write all new html files to /docs. Note docsrc (docs source) and docs are separate for version control and because github pages only lets the folder docs contain the website annoyingly. Some minor warnings may occur as to files in toctree to do with maxdepth. Needs fixing..

If the make compile runs with no errors the website should be upated. Then simply push to the main branch and the website will update remotely. May take a few minutes.
