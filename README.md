

| Ends with (excluding file extension) | Stands for | Usage/Meaning |
| - | - | - |
| -test | Test Version | This is where I actively work and for grading should be ignored |
| -rls | Release Version | This is a file that is known to work. For grading this file should be used |
<!--| -alp | Alpha Version | This is an unstable version of a file and has a critical issue |
| -bet | Beta Version | Only used in large projects, this is to indicate there is a known minor issue in said file, but is unlikely to be used, as calling a file is likely to be used in such a large project | -->
  
py-normal100.py = The version that has nothing that could be considered abuse  
py-normal90.py = The version that has nothing I consider to be abuse, but has 1 line compound statements written down in the same line as the statement, so, for example "for x in range(3): print(x)".  
py-abuse50.py = The version that has some abuse, mostly same as previous and semicolons for putting code inside previous lines  
py-abuse75.py = The version that has 2nd most abuse, everything found in previous versions and return value abuse of statements such as teleport, which allows for compound statements to be added in a semicolon line.  
py-warcrimes.py = Abuses so much that all previous transgressions and now also exec is put in a single file, which is a single line long.  
  
For py-normal90-stars-rls.py and py-normal100-stars-rls.py, these 2 are the only files containing night sky and stars.  
