# Official 2025 Carnegie Research Activity Designation (ACE + Indiana University)
# Source: en.wikipedia.org/wiki/List_of_research_universities_in_the_United_States
# R1 = 187 institutions, R2 = 139 institutions (as fetched 2026-11-10)
R1_RAW = """American University
Arizona State University
Auburn University
Baylor College of Medicine
Baylor University
Binghamton University
Boston College
Boston University
Brandeis University
Brigham Young University
Brown University
California Institute of Technology
Carnegie Mellon University
Case Western Reserve University
Catholic University of America
Clemson University
Colorado School of Mines
Colorado State University-Fort Collins
Columbia University in the City of New York
Cornell University
CUNY Graduate School and University Center
Dartmouth College
Drexel University
Duke University
East Carolina University
Emory University
Florida Atlantic University
Florida International University
Florida State University
George Mason University
George Washington University
Georgetown University
Georgia Institute of Technology-Main Campus
Georgia State University
Harvard University
Howard University
Indiana University Bloomington
Indiana University Indianapolis
Iowa State University
Johns Hopkins University
Kansas State University
Kent State University at Kent
Lehigh University
Louisiana State University and Agricultural & Mechanical College
Loyola University Chicago
Massachusetts Institute of Technology
Medical University of South Carolina
Michigan State University
Michigan Technological University
Mississippi State University
Missouri University of Science and Technology
Montana State University
New Jersey Institute of Technology
New Mexico State University-Main Campus
New York University
North Carolina State University at Raleigh
North Dakota State University-Main Campus
Northeastern University
Northern Arizona University
Northwestern University
Nova Southeastern University
Ohio State University-Main Campus
Ohio University-Main Campus
Oklahoma State University
Old Dominion University
Oregon State University
Princeton University
Purdue University
Rensselaer Polytechnic Institute
Rice University
Rutgers University-New Brunswick
Saint Louis University
San Diego State University
Southern Illinois University-Carbondale
Southern Methodist University
Stanford University
Stony Brook University
Syracuse University
Temple University
Texas A & M University-College Station
Texas Tech University
The Pennsylvania State University
The University of Alabama
The University of Montana
The University of Tennessee Health Science Center
The University of Tennessee-Knoxville
The University of Texas at Arlington
The University of Texas at Austin
The University of Texas at Dallas
The University of Texas at El Paso
The University of Texas at San Antonio
The University of Texas Health Science Center at Houston
The University of Texas Health Science Center at San Antonio
Tufts University
Tulane University of Louisiana
University at Albany
University at Buffalo
University of Alabama at Birmingham
University of Arizona
University of Arkansas
University of California, Berkeley
University of California, Davis
University of California, Irvine
University of California, Los Angeles
University of California, Merced
University of California, Riverside
University of California, San Diego
University of California, San Francisco
University of California, Santa Barbara
University of California, Santa Cruz
University of Central Florida
University of Chicago
University of Cincinnati
University of Colorado Boulder
University of Colorado Denver/Anschutz Medical Campus
University of Connecticut
University of Dayton
University of Delaware
University of Denver
University of Florida
University of Georgia
University of Hawaii at Manoa
University of Houston
University of Idaho
University of Illinois Chicago
University of Illinois Urbana-Champaign
University of Iowa
University of Kansas
University of Kentucky
University of Louisiana at Lafayette
University of Louisville
University of Maine
University of Maryland-Baltimore County
University of Maryland-College Park
University of Maryland, Baltimore
University of Massachusetts-Amherst
University of Massachusetts-Boston
University of Massachusetts-Lowell
University of Memphis
University of Miami
University of Michigan-Ann Arbor
University of Minnesota-Twin Cities
University of Mississippi
University of Missouri-Columbia
University of Missouri-Kansas City
University of Nebraska Medical Center
University of Nebraska-Lincoln
University of Nevada-Las Vegas
University of Nevada-Reno
University of New Hampshire-Main Campus
University of New Mexico-Main Campus
University of North Carolina at Chapel Hill
University of North Carolina at Charlotte
University of North Dakota
University of North Texas
University of Notre Dame
University of Oklahoma-Norman Campus
University of Oregon
University of Pennsylvania
University of Pittsburgh-Pittsburgh Campus
University of Rhode Island
University of Rochester
University of South Carolina-Columbia
University of South Florida
University of Southern California
University of Southern Mississippi
University of Texas Southwestern Medical Center
University of Toledo
University of Utah
University of Vermont
University of Virginia-Main Campus
University of Washington-Seattle Campus
University of Wisconsin-Madison
University of Wisconsin-Milwaukee
University of Wyoming
Utah State University
Vanderbilt University
Virginia Commonwealth University
Virginia Polytechnic Institute and State University
Washington State University
Washington University in St Louis
Wayne State University
Weill Cornell Medicine
West Virginia University
William & Mary
Worcester Polytechnic Institute
Yale University"""

R2_RAW = """Abilene Christian University
Air Force Institute of Technology Graduate School of Engineering & Management
Albert Einstein College of Medicine
Appalachian State University
Arkansas State University
Augusta University
Azusa Pacific University
Ball State University
Boise State University
Bowling Green State University
California State Polytechnic University, Pomona
California State University, Fresno
California State University, Fullerton
California State University, Long Beach
California State University, Los Angeles
California State University, Sacramento
Central Michigan University
Chapman University
Claremont Graduate University
Clark Atlanta University
Clark University
Clarkson University
Cleveland State University
Creighton University
CUNY City College
CUNY Hunter College
Delaware State University
DePaul University
Duquesne University
East Tennessee State University
East Texas A&M University
Eastern Michigan University
Eastern Virginia Medical School
Embry-Riddle Aeronautical University-Daytona Beach
Florida Agricultural and Mechanical University
Florida Institute of Technology
Fordham University
Georgia Southern University
Hampton University
Hofstra University
Icahn School of Medicine at Mount Sinai
Idaho State University
Illinois Institute of Technology
Illinois State University
Indiana University of Pennsylvania
Jackson State University
James Madison University
Kean University
Kennesaw State University
Lamar University
Loma Linda University
Long Island University
Louisiana State University Health Sciences Center, New Orleans
Louisiana State University New Orleans
Louisiana Tech University
Loyola Marymount University
Marquette University
Marshall University
Medical College of Wisconsin
Mercer University
Miami University, Oxford
Middle Tennessee State University
Montclair State University
Morgan State University
North Carolina A&T State University
Northern Illinois University
Oakland University
Oklahoma State University Center for Health Sciences
Oregon Health & Science University
Pepperdine University
Portland State University
Prairie View A&M University
Rochester Institute of Technology
Rockefeller University
Rowan University
Rush University
Rutgers University-Camden
Rutgers University-Newark
Saint Joseph's University
Sam Houston State University
San Francisco State University
San Jose State University
Seton Hall University
South Carolina State University
South Dakota State University
Southern Connecticut State University
Southern University
Stevens Institute of Technology
SUNY College of Environmental Science and Forestry
Tarleton State University
Teachers College, Columbia University
Tennessee State University
Tennessee Technological University
Texas A&M University-Corpus Christi
Texas A&M University-Kingsville
Texas Christian University
Texas Southern University
Texas State University
Texas Tech University Health Sciences Center
Texas Woman's University
The New School
The University of Texas at Tyler
The University of Texas Medical Branch at Galveston
The University of Texas Rio Grande Valley
The University of West Florida
Thomas Jefferson University
University of Akron Main Campus
University of Alabama, Huntsville
University of Alaska Fairbanks
University of Arkansas at Little Rock
University of Arkansas for Medical Sciences
University of Colorado Colorado Springs
University of Massachusetts Chan Medical School
University of Massachusetts Dartmouth
University of Michigan-Dearborn
University of Missouri-St. Louis
University of Nebraska Omaha
University of New England
University of North Carolina at Greensboro
University of North Carolina Wilmington
University of North Florida
University of Northern Colorado
University of Oklahoma-Health Sciences Center
University of Puerto Rico, Mayaguez
University of Puerto Rico, Rio Piedras
University of San Diego
University of San Francisco
University of South Alabama
University of South Dakota
University of Tulsa
Upstate Medical University
Villanova University
Virginia State University
Wake Forest University
West Chester University of Pennsylvania
Western Michigan University
Wichita State University
Wright State University
Yeshiva University"""

import re
def norm(s):
    s=(s or '').lower().strip()
    s=s.replace('a&m',' am ').replace('a & m',' am ')
    s=s.replace('&',' and ')
    s=re.sub(r'[.,/\-–—]',' ',s)
    s=re.sub(r'\b(the|at|of|and|campus|main|a)\b',' ',s)
    s=re.sub(r'\s+',' ',s).strip()
    return s

def build(raw):
    out=set()
    for line in raw.strip().split('\n'):
        out.add(norm(line))
    return out

R1=build(R1_RAW)
R2=build(R2_RAW)

# Build campus-stripped index so a dataset name without the campus token still matches.
def _core(name):
    t=name.split()
    while len(t)>2 and t[-1] in CAMPUS_TAIL:
        t=t[:-1]
    return ' '.join(t)
CAMPUS_TAIL={'station', 'county', 'bloomington', 'charlotte', 'angeles', 'pomona', 'boston', 'cities', 'denver', 'collins', 'milwaukee', 'newark', 'manoa', 'norman', 'vegas', 'twin', 'brunswick', 'city', 'chapel', 'greensboro', 'louis', 'lincoln', 'lafayette', 'baltimore', 'park', 'pittsburgh', 'wilmington', 'lowell', 'arbor', 'dearborn', 'carbondale', 'fullerton', 'raleigh', 'dartmouth', 'indianapolis', 'worcester', 'camden', 'amherst', 'knoxville', 'ann', 'columbia', 'fairbanks', 'anchorage', 'college', 'madison', 'st', 'boulder', 'fayetteville', 'edwardsville', 'fresno', 'seattle', 'reno', 'fort', 'hill', 'asheville', 'flint', 'louisville', 'sacramento', 'honolulu', 'collegestation', 'springs', 'kansas', 'omaha'}
R1_CORE={_core(x):x for x in R1}
R2_CORE={_core(x):x for x in R2}


# Manual aliases: dataset name -> canonical designation
# (covers short forms that normalization alone won't collapse)
ALIAS={
 'university of michigan':'R1',            # Ann Arbor
 'texas a and m university':'R1',          # College Station
 'penn state university':'R1',
 'pennsylvania state university':'R1',
 'louisiana state university':'R1',        # LSU main
 'university of texas austin':'R1',
 'university of wisconsin':'R1',           # Madison (default main)
 'university of colorado':'R1',
 'university of missouri':'R1',            # Columbia
 'university of nebraska':'R1',            # Lincoln
 'university of massachusetts':'R1',       # Amherst
 'university of maryland':'R1',            # College Park
 'university of minnesota':'R1',
 'university of california berkeley':'R1',
 'virginia tech':'R1',
 'ohio state university':'R1',
 'indiana university':'R1',                # Bloomington
 'rutgers university':'R1',                # New Brunswick
 'university of pittsburgh':'R1',
 'university of washington':'R1',          # Seattle
 'suny buffalo':'R1',
 'suny albany':'R1',
 'suny stony brook':'R1',
 'washington university st louis':'R1',
 'william and mary':'R1',
 'college william and mary':'R1',
 'city college of new york':'R2',
 'city college new york':'R2',
 'texas am university':'R1',
 'texas am university college station':'R1',
 'north carolina state university':'R1',
 'university south carolina':'R1',
 'purdue':'R1',
 'purdue university':'R1',
 'uci':'R1',
 'ucla':'R1',
 'ucsd':'R1',
 'ucsb':'R1',
 'ucf':'R1',
 'usc':'R1',
 'uc berkeley':'R1',
 'uc davis':'R1',
 'uc irvine':'R1',
 'uc riverside':'R1',
 'uc santa barbara':'R1',
 'uc santa cruz':'R1',
 'uc merced':'R1',
 'uc san diego':'R1',
 'harvard seas':'R1',
 'harvard':'R1',
 'mit':'R1',
 'caltech':'R1',
 'cmu':'R1',
 'gatech':'R1',
 'georgia tech':'R1',
 'nyu':'R1',
 'rutgers state university new jersey':'R1',
 'rutgers':'R1',
 'njit':'R1',
 'rpi':'R1',
 'wpi':'R1',
 'rit':'R2',
 'uic':'R1',
 'uiuc':'R1',
 'uw madison':'R1',
 'uw seattle':'R1',
 'asu':'R1',
 'osu':'R1',
 'psu':'R1',
 'vt':'R1',
 'vcu':'R1',
 'utsa':'R1',
 'utd':'R1',
 'utep':'R1',
 'ut arlington':'R1',
 'ut austin':'R1',
 'ut dallas':'R1',
 'tamu':'R1',
 'texas a and m university':'R1',
 'wustl':'R1',
 'washu':'R1',
 'jhu':'R1',
 'unc':'R1',
 'unc chapel hill':'R1',
 'uconn':'R1',
 'umbc':'R1',
 'umd':'R1',
 'umass':'R1',
 'umass amherst':'R1',
}

ALIAS={norm(k):v for k,v in ALIAS.items()}

def carnegie(inst):
    n=norm(inst)
    if n in R1: return 'R1'
    if n in R2: return 'R2'
    if n in R1_CORE: return 'R1'
    if n in R2_CORE: return 'R2'
    if n in ALIAS: return ALIAS[n]
    tokset=set(n.split())
    # also try stripping the dataset's own trailing campus/geo token for core match
    _branch_tail={'edwardsville','flint','dearborn','texarkana','stout','kingsville',
        'corpus','permian','tyler','monroe','shreveport','huntsville','pembroke',
        'asheville','greensboro','wilmington','northridge','fullerton','pomona',
        'bakersfield','stanislaus','bernardino','marcos','springfield','camden','newark'}
    _t=n.split()
    if _t and _t[-1] not in _branch_tail:
        nc=_core(n)
        if nc in R1_CORE or nc in R1: return 'R1'
        if nc in R2_CORE or nc in R2: return 'R2'
    BRANCH={'flint','dearborn','texarkana','stout','edwardsville','springfield',
            'global','southern','northern','eastern','western','wesleyan','christian',
            'pembroke','asheville','greensboro','wilmington','charlotte','huntsville',
            'tyler','permian','corpus','kingsville','commerce','galveston','rio',
            'pomona','fullerton','northridge','bakersfield','chico','stanislaus',
            'bay','marcos','bernardino','monterey','humboldt','maritime',
            'denver','colorado springs','boulder','anschutz','monroe','shreveport',
            'crookston','duluth','morris','rochester','camden','newark',
            'north','south','east','west','central','downtown','polytechnic','poly'}
    def ok(cand):
        ct=set(cand.split())
        if not ct<=tokset: return False
        if (tokset-ct) & BRANCH: return False
        return len(ct)>=3
    for cand in R1:
        if ok(cand): return 'R1'
    for cand in R2:
        if ok(cand): return 'R2'
    return None
