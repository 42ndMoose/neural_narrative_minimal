
import json
import uuid
from models import make_session, Statement, Edge, Container, ContainerStatement

def uid(prefix):
    return f"{prefix}-{uuid.uuid4().hex}"

db = make_session("sqlite:///kg.db")

# Wipe existing (simple dev reset)
db.query(ContainerStatement).delete()
db.query(Edge).delete()
db.query(Statement).delete()
db.query(Container).delete()
db.commit()

# Helper to insert statements
def add_stmt(id, text, type="claim", scope=None, time_as_of=None, actors=None, status="live", tags=None):
    s = Statement(
        id=id,
        text=text,
        type=type,
        scope=scope,
        time_as_of=time_as_of,
        actors_json=json.dumps(actors or []),
        status=status,
        tags_json=json.dumps(tags or [])
    )
    db.add(s)
    return s

def add_edge(from_id, to_id, relation, note=None, id=None):
    e = Edge(
        id=id or uid("E"),
        from_id=from_id,
        to_id=to_id,
        relation=relation,
        note=note
    )
    db.add(e)
    return e

# ---- Statements (subset from your narrative) ----
pairs = []

S = {}

def S_add(key, **kwargs):
    S[key] = kwargs["id"]
    add_stmt(**kwargs)

# Section 0
S_add("S0.1", id="S0.1", text="Donald Trump is serving again as US president (45th and 47th) since 2025-01-20.", type="event", scope="US federal", time_as_of="2025-01-20", actors=["Trump"])
S_add("S0.2", id="S0.2", text="Trump’s second term targets DEI rollback, anti-ESG, fossil expansion, tariff leverage, and pushback against post-2016 censorship stacks.", type="policy", scope="US federal", actors=["Trump"])

# Section 1
S_add("S1.0", id="S1.0", text="It’s an elite civil war inside one shared machine, not one cabal.", type="takeaway")
S_add("S1.1", id="S1.1", text="Bloc A: Davos/WEF/ESG/DEI with legacy media, NGOs, universities, regulators aligned.", type="definition")
S_add("S1.2", id="S1.2", text="Bloc B: America-First/resource-capital aligned with tariffs, fossil fuels, sovereignty.", type="definition")
S_add("S1.3", id="S1.3", text="Both blocs still operate within the dollar/courts/bureaucracy/platform/supply-chain machine.", type="explanation")

# Section 2
S_add("S2.0", id="S2.0", text="The Big Three are anchor shareholders across major media parents, though not omnipotent.", type="takeaway")
S_add("S2.1", id="S2.1", text="Comcast (NBC/MSNBC/CNBC) lists Vanguard, BlackRock, State Street near the top institutional holders.", type="claim")
S_add("S2.2", id="S2.2", text="Disney (ABC/ESPN) has the Big Three among top holders.", type="claim")
S_add("S2.3", id="S2.3", text="Warner Bros. Discovery (CNN) shows significant Big Three holdings.", type="claim")
S_add("S2.4", id="S2.4", text="Fox Corp uses dual-class; Murdoch trust controls; Big Three are top holders of Class A.", type="claim")

# Section 3
S_add("S3.0", id="S3.0", text="The asset-management layer ties directly into WEF governance.", type="takeaway")
S_add("S3.1", id="S3.1", text="BlackRock is a WEF strategic partner; Larry Fink co-chairs the WEF board.", type="claim", actors=["BlackRock","WEF","Larry Fink"])
S_add("S3.2", id="S3.2", text="State Street publicly partners with WEF and participates at Davos.", type="claim", actors=["State Street","WEF"])
S_add("S3.3", id="S3.3", text="Vanguard participates in WEF parity/DEI initiatives.", type="claim", actors=["Vanguard","WEF"])

# Section 4
S_add("S4.0", id="S4.0", text="Shareholders set board-level incentives; managers/talent drive editorial outcomes.", type="takeaway")
S_add("S4.1", id="S4.1", text="Big Three stewardship affects governance themes; they don't pick daily segments.", type="explanation")
S_add("S4.2", id="S4.2", text="Tucker’s exit came from Fox management amid legal risk; Big Three were background shareholders.", type="case")
S_add("S4.3", id="S4.3", text="Pro-Trump hosts persist if profitable and non-catastrophic legally.", type="case")

# Section 5
S_add("S5.0", id="S5.0", text="Regulators + NGOs/academia + brand-safety + platforms standardize allowed narratives.", type="takeaway")
S_add("S5.1", id="S5.1", text="UK Ofcom + Online Safety Act enable deep platform oversight and fines.", type="claim", scope="UK")
S_add("S5.2", id="S5.2", text="BBC licence enforcement is state-backed with warrant pathway.", type="claim", scope="UK")
S_add("S5.3", id="S5.3", text="Canada’s CBC/CRTC structure ties broadcasting/streaming to federal levers.", type="claim", scope="Canada")
S_add("S5.4", id="S5.4", text="TNI/EIP/DFRLab/IFCN feed platform moderation pipelines.", type="claim")
S_add("S5.5", id="S5.5", text="GARM/WFA brand-safety norms steer ad dollars away from non-aligned content.", type="claim")

# Section 6
S_add("S6.0", id="S6.0", text="ESG/net-zero remains strong globally; US legal pushback forces hedging.", type="takeaway")
S_add("S6.1", id="S6.1", text="Vanguard exited NZAM in 2022.", type="event", actors=["Vanguard"])
S_add("S6.2", id="S6.2", text="BlackRock and others softened alliance posture under GOP pressure.", type="claim", actors=["BlackRock"])
S_add("S6.3", id="S6.3", text="WEF board includes Larry Fink; WEF promotes net-zero/DEI/stakeholder capitalism.", type="claim", actors=["WEF","Larry Fink"])

# Section 7
S_add("S7.0", id="S7.0", text="Aligned incentives (regs, NGOs, brands, investors, platforms) synchronize narratives without a central boss.", type="takeaway")

# Section 8
S_add("S8.0", id="S8.0", text="Trump targets specific pillars: DEI rollback, climate alliances, fossil expansion, tariffs.", type="takeaway", actors=["Trump"])
S_add("S8.1", id="S8.1", text="EO 14151—DEI rollback agenda across federal and contractors.", type="policy", scope="US federal", actors=["Trump"])
S_add("S8.2", id="S8.2", text="EO 14156—National Energy Emergency; accelerate fossil approvals; weaken climate regs.", type="policy", scope="US federal", actors=["Trump"])
S_add("S8.3", id="S8.3", text="Tariffs used as leverage to reset supply chains toward US production.", type="policy", scope="US/world", actors=["Trump"])
S_add("S8.4", id="S8.4", text="Trump uses Davos as a hostile venue to sell US growth, tariffs, and fossil revival.", type="claim", actors=["Trump","WEF"])

# Section 9
S_add("S9.0", id="S9.0", text="Accountability is slow due to statutes, venue, bureaucracy, and standards of proof.", type="takeaway")
S_add("S9.1", id="S9.1", text="Pam Bondi as AG targets narrow, provable charges (e.g., on Comey) over grand RICO plays.", type="claim", scope="US federal", actors=["Pam Bondi","DOJ"])
S_add("S9.2", id="S9.2", text="Not everything disliked is a crime; statutes and venues constrain prosecutions.", type="explanation", scope="US")
S_add("S9.3", id="S9.3", text="Congressional subpoenas expose but DOJ controls indictments; timelines drag.", type="explanation", scope="US")

# Section 10
S_add("S10.0", id="S10.0", text="He’s amplified because split elites + profit; he can’t break the chains because the system is multi-layered.", type="takeaway")
S_add("S10.1", id="S10.1", text="Profit and ownership hedging keep Trump uncut on air.", type="explanation")
S_add("S10.2", id="S10.2", text="Dollar/markets/bureaucracy/courts/media/NGO stack constrains total rupture.", type="explanation")

# Section 11
S_add("S11.0", id="S11.0", text="Civil war inside one machine; Big Three–WEF link; compliance stack; Trump attacks pillars; courts/DOJ constraints remain.", type="summary")

db.commit()

# ---- Edges ----
def sup(a,b): add_edge(S[a], S[b], "supports")
def dep(a,b): add_edge(S[a], S[b], "depends_on")
def sumz(a,b): add_edge(S[a], S[b], "summarizes")

# Section 1 links
sup("S1.1","S1.0"); sup("S1.2","S1.0"); sup("S1.3","S1.0")

# Section 2 links
for k in ["S2.1","S2.2","S2.3","S2.4"]:
    sup(k,"S2.0")

# Section 3 links
for k in ["S3.1","S3.2","S3.3"]:
    sup(k,"S3.0")

# Section 4 links
for k in ["S4.1","S4.2","S4.3"]:
    sup(k,"S4.0")

# Section 5 links
for k in ["S5.1","S5.2","S5.3","S5.4","S5.5"]:
    sup(k,"S5.0")

# Section 6 links
for k in ["S6.1","S6.2","S6.3"]:
    sup(k,"S6.0")

# Section 7 links
# (S7.0 is a standalone takeaway for now)

# Section 8 links
for k in ["S8.1","S8.2","S8.3","S8.4"]:
    sup(k,"S8.0")
dep("S8.1","S0.1")

# Section 9 links
for k in ["S9.1","S9.2","S9.3"]:
    sup(k,"S9.0")

# Section 10 links
sup("S10.1","S10.0"); sup("S10.2","S10.0"); dep("S10.2","S1.3")

# Section 11 links
for k in ["S1.0","S2.0","S3.0","S5.0","S8.0","S9.0"]:
    sumz("S11.0", k)

db.commit()

# ---- Container ----
c = Container(
    id="C-001",
    slug="trump-elite-compliance",
    title="Trump’s Second Term, Elite Factions, Legacy Media, and the Compliance Stack",
    intro="Atomic statements with explicit relations. Read the default path like an article or branch into supporting links.",
    root_ids_json=json.dumps(["S0.1","S1.0","S2.0","S5.0","S8.0","S10.0"]),
    default_path_json=json.dumps(["S1.0","S2.0","S3.0","S5.0","S8.0","S10.0","S11.0"])
)
db.add(c)
db.commit()

# Attach statements to container (simple: include all we inserted)
for key, sid in S.items():
    db.add(ContainerStatement(id=uid("CS"), container_id=c.id, statement_id=sid))
db.commit()

print("Seed complete.")
