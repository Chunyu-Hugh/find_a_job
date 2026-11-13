# Official HBCU list — U.S. Dept. of Education, White House Initiative on HBCUs
# Source: sites.ed.gov/whhbcu (the "105 HBCUs" roster), fetched 2026-11-13.
# Used as an independent flag (a school can be both R1 and HBCU, e.g. Howard).
from carnegie2025 import norm

HBCU_RAW = """Alabama A&M University
Alabama State University
Bishop State Community College
Gadsden State Community College
H Councill Trenholm State Community College
J. F. Drake State Community and Technical College
Lawson State Community College
Miles College
Oakwood University
Shelton State Community College
Stillman College
Talladega College
Tuskegee University
Arkansas Baptist College
Philander Smith College
Shorter College
University of Arkansas at Pine Bluff
Delaware State University
Howard University
University of the District of Columbia
Bethune-Cookman University
Edward Waters College
Florida Agricultural and Mechanical University
Florida Memorial University
Albany State University
Clark Atlanta University
Fort Valley State University
Interdenominational Theological Center
Morehouse College
Morehouse School of Medicine
Paine College
Savannah State University
Spelman College
Kentucky State University
Simmons College of Kentucky
Dillard University
Grambling State University
Southern University and A&M College
Southern University at New Orleans
Southern University at Shreveport
Xavier University of Louisiana
Bowie State University
Coppin State University
Morgan State University
University of Maryland Eastern Shore
Alcorn State University
Coahoma Community College
Jackson State University
Mississippi Valley State University
Rust College
Tougaloo College
Harris-Stowe State University
Lincoln University Missouri
Bennett College
Elizabeth City State University
Fayetteville State University
Johnson C Smith University
Livingstone College
North Carolina A&T State University
North Carolina Central University
Saint Augustine's University
Shaw University
Winston-Salem State University
Central State University
Wilberforce University
Langston University
Cheyney University of Pennsylvania
Lincoln University Pennsylvania
Allen University
Benedict College
Claflin University
Clinton College
Denmark Technical College
Morris College
South Carolina State University
Voorhees College
American Baptist College
Fisk University
Lane College
Le Moyne-Owen College
Meharry Medical College
Tennessee State University
Huston-Tillotson University
Jarvis Christian College
Paul Quinn College
Prairie View A&M University
Southwestern Christian College
Texas College
Texas Southern University
Wiley College
University of the Virgin Islands
Hampton University
Norfolk State University
Virginia State University
Virginia Union University
Virginia University of Lynchburg
Bluefield State College
West Virginia State University"""

# Lincoln University appears in two states (MO, PA) with different norms; the
# generic norm() collapses "university"/"missouri" fine because we keep the
# state word in these two entries above.
HBCU = {norm(x) for x in HBCU_RAW.strip().split("\n")}

# A couple of common dataset spellings that norm() alone won't collapse.
HBCU_ALIAS = {
    norm("Florida A&M University"): True,         # FAMU
    norm("North Carolina A&T"): True,
    norm("NC A&T State University"): True,
    norm("Texas Southern"): True,
    norm("Prairie View A&M"): True,
    norm("Southern University"): True,            # Baton Rouge main
    norm("UDC"): True,
}

def is_hbcu(inst):
    n = norm(inst)
    if n in HBCU:
        return True
    if n in HBCU_ALIAS:
        return True
    # Fallback for minor spelling drift only. Require the dataset name and an
    # HBCU entry to be nearly the SAME token set (symmetric), not one a subset
    # of the other. A one-sided subset wrongly matches e.g. "Albany State
    # University" (HBCU) to "State University of New York at Albany" (not HBCU),
    # or "West Virginia State University" (HBCU) to "...West Virginia
    # University" (not HBCU). Symmetric match avoids those.
    # A single extra word in the dataset name that is a place/qualifier means a
    # DIFFERENT school (Central State U. vs Central CONNECTICUT State U.), so an
    # extra token from this set blocks the fallback match.
    QUALIFIER = {"connecticut", "northern", "southern", "eastern", "western",
                 "north", "south", "east", "west", "new", "york", "potomac"}
    toks = n.split()
    tokset = set(toks)
    for cand in HBCU:
        ct = set(cand.split())
        if len(ct) < 3:
            continue
        if ct <= tokset:                         # every HBCU token present
            extra = tokset - ct
            if not extra:
                return True
            if len(extra) == 1 and not (extra & QUALIFIER):
                return True
    return False
