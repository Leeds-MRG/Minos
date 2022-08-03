# Compiling Page 

Github page is writting using sphinx and the readthedocs.io theme. To recompile the website locally make any changes in the docsrc folder to the toc tree and html files.

When changes are made run

make github

in /docsrc. Should write all new html files to /docs. Note docsrc (docs source) and docs are separate for version control and because github pages only lets the folder docs contain the website annoyingly. 

If the make compile runs with no errors the website should be upated. Then simply push to the main branch and the website will update remotely. May take a few minutes.
