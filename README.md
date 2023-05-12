# Penn Innovation Ecosystem
In the terminal, run command line:
bokeh serve --show network_viz.py \\
(debug)BOKEH_MINIFIED=no bokeh serve --dev --show network_viz.py

Penn Innovation Ecosystem (PIE)

Wharton faculty has produced path-breaking research on innovation ecosystems, which the Mack Institute aims to translate for the benefit of Penn’s own innovation ecosystem. Visualizing the ecosystem is the first step towards this goal. Our PIE Visualization Tool depicts the ecosystem as a network of innovation-relevant nodes connected by directed ties among them.
We distinguish among five types of innovation nodes that are not mutually exclusive: Research & Development (R&D), Teaching, Organizer of innovation activities, Knowledge repository, and Media, which covers on-campus innovations for the general public. We assembled Penn’s 70 innovation nodes by searching the Penn website for pages with the word “innovation” and identifying the organizational units that the pages represent.

There is a relationship between two innovation nodes if one of them (source) embeds a link to the other (target) on its website. Thus, the link signifies the relevance of the target to the source as a provider of information, innovation partner, communication channel, etc.
The PIE Visualization Interface

- By default, the diagram shows the full network with all the nodes and relationships among them. You can always restore it by clicking “Reset Full Network.”
- All the professional schools at Penn discuss innovation on their websites and, arguably, are engaged in both R&D and teaching of innovations. To explore a network without schools, click on “Exclude schools from network”.
- To get information about an innovation node
    - hover over the node until an icon appears
    - enable Tap functionality from the Toolbar, and click on the weblink on the icon
- To explore the network between specific sources and targets
    - list them individually in the windows “Select Source Node(s)” and “Select Target Node(s)” using attached pull-down menus
    - click “Generate”
- To explore the network between specific types of innovation nodes
    - choose nodes by clicking on the corresponding buttons under “Select Source Type(s)” and “Select Target Type(s)”
    - click “Generate”


Jira: https://mackinstitute.atlassian.net/jira/software/projects/RMP/boards/9
1.	Data Collection

From Google search results by searching for “site:upenn.edu “innovation””, 388 links are collected and saved in the total_links.csv. 10 of the URL links are in PDF format, and we excluded them from the list.

The following links (16 members of Ecosystem Penn) and other innovation-relevant units are added to total_links.csv, including the URLs of schools, departments, and other organizations: https://www.sas.upenn.edu/, https://venturelab.upenn.edu/, https://www.asc.upenn.edu/, https://www.dental.upenn.edu/, https://www.design.upenn.edu/, https://www.gse.upenn.edu/, https://www.seas.upenn.edu/, https://www.law.upenn.edu/, https://www.med.upenn.edu/, https://www.nursing.upenn.edu/, https://www.sp2.upenn.edu/, https://www.vet.upenn.edu/, https://www.library.upenn.edu/, https://www.chop.edu/, https://sciencecenter.org/, https://wistar.org/. 
In total, there are 407 unique “seed” URL links.

2.	Domain Extraction and Filtering

From each URL link, we extracted the domain and saved the domain as a column for future data analysis. For example, https://www.nursing.upenn.edu/innovation/ as one of the links in the total_links.csv, https://www.nursing.upenn.edu is the domain and is saved in the column domains_clickable for manual examination, and nursing.upenn.edu is saved in the column domains_clean for network analysis.
We observed that websites could contain the content of innovation but not necessarily serve as an innovation unit, which is in the scope of our interest. Therefore, we exclude them from the list of domains. The following links are manually examined and excluded from the domain list: 

https://catalog.upenn.edu, https://curf.upenn.edu, https://hub.provost.upenn.edu, https://www.business-services.upenn.edu, https://www.collegehouses.upenn.edu,  https://www.elp.upenn.edu, https://www.hr.upenn.edu, https://www.upenn.edu, 
https://apps.wharton.upenn.edu, https://ware.house.upenn.edu,  https://undergrad-inside.wharton.upenn.edu, https://global.upenn.edu.
There are 70 unique domains that we identified as innovation units.

3.	Categorization of domain

We distinguish among five types of innovation nodes that are not mutually exclusive: Research & Development (R&D), Teaching, Organizer of innovation activities, Knowledge repository, and Media, which covers on-campus innovations for the general public.
The full list of categorization of domain is located in the PennEcosystem/bokeh-app/data/site_domainV2.xlsx domain tab with label of 1.

4.	Network 

From each URL links, we aggregated the embedded links and saved the URL links which belong to the domains we collected in step 2. The output file includes three columns: a source (which is a seed URL link), a target (which is an embedded link on the seed URL), and weight (the number of times that the source point to target).
The full list of network is located in the PennEcosystem/bokeh-app/data/network.csv on Github.

5.	Visualization

We used python library Networkx for drawing building the network and Bokeh for visualizing the network. We created a dashboard for the users to interactively visualize the network. Features of the interactive dashboard include:
- Category filter: The category filters allow multiple selections for both source and target types. A user would need to select both source and target types to include the units of corresponding types.
- Innovation unit filter: The unit filters allow multiple selections for both source and target at an individual level. A user would need to select both source and target categories to include the units of corresponding categories.
- Remove schools: The button ‘remove schools’ when clicked/highlighted excludes schools from the network.
- Network metrics and analysis: deployed using networkx 

6.	Web development

For deployment, there are two ways to run the dashboard: local Python server and rendered html file. To run the dashboard, go to terminal and run bokeh serve --show network_viz.py.
For debugging, run BOKEH_MINIFIED=no bokeh serve --dev --show network_viz.py.

Next Step:
For now, the Generate buttom works after reset each time and doesn't allow continuous generation with filters. More investigation is required on the 'callback' functon in network_viz.py.
For long-term development of the project, we explored the index of upenn.edu domain and recommend scrape the data using the top-to-buttom search instead of google search resutls.

Limitations and Improvement:
Our original idea was to go through each page under upenn.edu domain and download relevant content. But we didn’t find an index to all Penn websites.

Appendix:

Ecosystem Penn members includes:
School of Arts & Sciences, The Wharton School/Venture Lab, Annenberg School of Communications, School of Dental Medicine, Stuart Weizman School of Design,  Graduate School of Education, School of Engineering of Applied Science, Penn Carey Law, Perelman School of Medicine, School of Nursing, School of Social Policy & Practice, School of Veterinary Medicine, Penn Center for Innovation, Penn Libraries, Children’s Hospital of Philadelphia, Science Center, The Wistar Institute.

Helpful Recourse:
Networkx Python library for generating network:
https://networkx.org/documentation/stable/tutorial.html
Network Analysis:
https://programminghistorian.org/en/lessons/exploring-and-analyzing-network-data-with-python - centrality
Egocentric Network Analysis(accessible through Penn Library):
https://www.cambridge.org/core/books/egocentric-network-analysis/D241B6D07F1A5C760657F252FAD65A4C