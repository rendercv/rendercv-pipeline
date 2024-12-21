<!-- Remove below in src/markdown/Header.j2.md not in README.md -->

# RenderCV Pipeline

Are you ready to revolutionize the way you manage and craft your CVs and resumes?

Picture this:

1.  You simply update your `src/John_Doe_CV.yaml` input file and push the changes.
2.  Then, a pipeline generates a new PDF and Markdown from it and uploads it to the repository.
3.  When you are done with your work, you can create a new release on GitHub, tagging your CV with something like `v2024.04`. The pipeline will automatically add the PDF and its $\LaTeX$ source as assets to the release.
4.  You have successfully created your CV pipeline, and all the history is in safe hands and reproducible.

**How to start?**

1.  [Click here](https://github.com/new?template_name=rendercv-pipeline&template_owner=sinaatalay) to create your CV repository based on this `rendercv-pipeline` template repository.
2.  Edit either
    -  the `src/John_Doe_CV.yaml` file, or
    -  the contents of `src/markdown` or `src/classic` directories
    
    and push. Then, see the magic happen.

**Some tips**

-  Learn more about [RenderCV](https://github.com/sinaatalay/rendercv) to understand what you can do with this tool.
-  Edit and preview your CV in your browser without installing anything by creating a codespace. Click the <> **Code** button, then click the **Codespaces** tab, and then click **Create codespace on main**. The environment will be ready for RenderCV usage. Update `.vscode/launch.json` to point to your YAML file and press `F5` to run RenderCV in the browser.

<!-- Remove above in src/markdown/Header.j2.md not in README.md -->
# Fabio Calefato's CV

- Phone: +39 080 571 2213
- Email: [fabio.calefato@uniba.it](mailto:fabio.calefato@uniba.it)
- Location: Bari, Italy
- Website: [yourwebsite.com](https://yourwebsite.com/)
- LinkedIn: [fcalefato](https://linkedin.com/in/fcalefato)
- GitHub: [bateman](https://github.com/bateman)


# Welcome to RenderCV!

[RenderCV](https://rendercv.com) is a LaTeX-based CV/resume version-control and maintenance app. It allows you to create a high-quality CV or resume as a PDF file from a YAML file, with **Markdown syntax support** and **complete control over the LaTeX code**.

The boilerplate content was inspired by [Gayle McDowell](https://github.com/dnl-blkv/mcdowell-cv).

# Quick Guide

- Each section title is arbitrary and each section contains a list of entries.
- There are 7 unique entry types: *BulletEntry*, *TextEntry*, *EducationEntry*, *ExperienceEntry*, *NormalEntry*, *PublicationEntry*, and *OneLineEntry*.
- Select a section title, pick an entry type, and start writing your section!
- [Here](https://docs.rendercv.com/user_guide/), you can find a comprehensive user guide for RenderCV.
# Education

## University of Pennsylvania, BS in Computer Science

- Sept 2000 – May 2005
- GPA: 3.9/4.0 ([a link to somewhere](https://example.com))
- **Coursework:** Computer Architecture, Comparison of Learning Algorithms, Computational Theory

# Experience

## Apple, Software Engineer

- June 2005 – Aug 2007
- Cupertino, CA
- Reduced time to render user buddy lists by 75% by implementing a prediction algorithm
- Integrated iChat with Spotlight Search by creating a tool to extract metadata from saved chat transcripts and provide metadata to a system-wide search database
- Redesigned chat file format and implemented backward compatibility for search

## Microsoft, Software Engineer Intern

- June 2003 – Aug 2003
- Redmond, WA
- Designed a UI for the VS open file switcher (Ctrl-Tab) and extended it to tool windows
- Created a service to provide gradient across VS and VS add-ins, optimizing its performance via caching
- Built an app to compute the similarity of all methods in a codebase, reducing the time from $$\mathcal{O}(n^2)$$ to $$\mathcal{O}(n \log n)$$
- Created a test case generation tool that creates random XML docs from XML Schema
- Automated the extraction and processing of large datasets from legacy systems using SQL and Perl scripts

# Publications

## 3D Finite Element Analysis of No-Insulation Coils ([10.1109/TASC.2023.3340648](https://doi.org/10.1109/TASC.2023.3340648))
- Jan 2004
- Frodo Baggins, ***John Doe***, Samwise Gamgee

# Projects

## Multi-User Drawing Tool

- [github.com/name/repo](https://github.com/rendercv/rendercv)
- Developed an electronic classroom where multiple users can simultaneously view and draw on a "chalkboard" with each person's edits synchronized
- Tools Used: C++, MFC

## Synchronized Desktop Calendar

- [github.com/name/repo](https://github.com/rendercv/rendercv)
- Developed a desktop calendar with globally shared and synchronized calendars, allowing users to schedule meetings with other users
- Tools Used: C#, .NET, SQL, XML

## Custom Operating System

- 2002
- Built a UNIX-style OS with a scheduler, file system, text editor, and calculator
- Tools Used: C

# Technologies

- Languages: C++, C, Java, Objective-C, C#, SQL, JavaScript
- Technologies: .NET, Microsoft SQL Server, XCode, Interface Builder
