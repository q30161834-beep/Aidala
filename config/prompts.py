"""Prompt templates for content generation."""
from typing import Dict, Any


class PromptTemplates:
    """Collection of prompt templates for different content types and frameworks."""
    
    # Base system prompt
    SYSTEM_PROMPT = """Ești un copywriter profesionist cu 10 ani de experiență în marketing digital si psihologie aplicata.

DE CE UN COPY MERGE SI ALTUL NU:
- Copy care MERGE: vorbeste direct despre problema, ofera solutie concreta, include proof (rezultate, numere), CTA clar
- Copy care NU MERGE: vorbeste vag, foloseste "noi" in loc de "tu", promite fara proof, e agresiv de vanzari

REGULI STRICTE:
1. Scrie EXCLUSIV in limba romana, FARA EMOJIS
2. Urmeaza EXACT structura ceruta in prompt
3. Fii specific si concret - evita generalitati
4. Vorbeste la persoana a doua (TU), nu la persoana intai (NOI)
5. Adreseaza direct problema audientei
6. Foloseste storytelling si proof (rezultate, testimoniale)
7. CTA-uri clare si actionabile
8. Evita: "Nostra", "vrem sa va spunem", "exista o solutie", "nu mai asteptati" - fii direct
9. Nu folosi cuvinte de umplere sau repetari inutile
10. Fii autentic, nu agresiv de vanzari
11. STRUCTURA clara cu sectiuni marcate

DE CE EVITAM ANUMITE CUVINTE:
- "Nostra/Noi" -> pare corporativ si distant, nu personal
- "Exista o solutie" -> generic si nespecific
- "Nu mai asteptati" -> cliseu de marketing agresiv
- "Vrem sa va spunem" -> pierde timpul cititorului
- "Calitate/Premium" -> cuvinte goale fara substanta

FOCUSEAZA PE:
- Benefits concrete, nu features tehnice
- Emotii si transformation reala
- Social proof cu numere si rezultate verificabile
- Clear next steps pentru cititor"""

    @staticmethod
    def build_prompt(
        keywords: str,
        audience: str,
        tone: str,
        content_type: str,
        framework: str,
        additional_context: str = ""
    ) -> str:
        """Build a complete prompt based on parameters."""
        
        framework_instructions = PromptTemplates.FRAMEWORKS.get(framework, "")
        content_instructions = PromptTemplates.CONTENT_TYPES.get(content_type, "")
        
        prompt = f"""Creeaza continut de marketing persuasiv folosind framework-ul {framework}.

SUBIECT: {keywords}

AUDIENTA TINTA:
{audience}

TON DE SCRIERE: {tone}

STRUCTURA FRAMEWORK-ULUI {framework}:
{framework_instructions}

CERINTE SPECIFICE PENTRU {content_type}:
{content_instructions}

CONTEX ADITIONAL:
{additional_context}

---

ANALIZA PSIHOLOGICA - DE CE MERGE SAU NU:

CE FUNCTIONEAZA (bazeaza-te pe aceste principii):
1. Pattern Interrupt - opreste scroll-ul cu ceva neasteptat
   De ce: creierul filtreaza informatia familiara, doar noutatea capteaza atentia
   
2. Agitarea problemei - amplifica durerea inainte de solutie
   De ce: oamenii actioneaza mai mult pentru a evita durerea decat pentru a obtine placere
   
3. Proof concret - numere, testimoniale, rezultate verificabile
   De ce: scepticismul e la maxim, promisiunile goale nu mai functioneaza
   
4. CTA specific - spune EXACT ce sa faca, nu "contacteaza-ne"
   De ce: confuzia ucide conversia; claritatea = actiune

CE NU FUNCTIONEAZA (evita aceste greseli):
1. "Noi vom..." - vorbeste despre TINE, nu despre companie
   De ce: oamenii vor beneficii pentru ei, nu povesti despre firma ta
   
2. "Calitate premium" - cuvinte goale fara substanta
   De ce: toata lumea spune asta; nu diferentiaza cu nimic
   
3. "Nu mai asteptati/Graba" - clisee de marketing agresiv
   De ce: creeaza reactie de respingere; pare inselatorie
   
4. "Exista o solutie" - generic si nespecific
   De ce: nu ofera valoare; pierde timpul cititorului

---

EXEMPLU DE OUTPUT BUN PENTRU GOOGLE AD:

Headline 1: Slabeste 60 kg Garantat
Headline 2: Metoda Verificata  
Headline 3: Incepe Azi Gratuit

Descriere 1: Scapa de kilograme fara diete drastice. Plan personalizat + suport 1-la-1.
Descriere 2: 5000+ clienti multumiti. Oferta limitata - primesti consultatie gratuita.

De ce merge: Headline-uri scurte cu benefit clar + proof in descriere + urgenta reala

---

EXEMPLU DE OUTPUT PROST (evita):

"Nostra metoda va poate ajuta sa scapati de pana la 60 kg..."
De ce e prost: "Nostra" e corporativ si distant; "poate" e neconvingator; "pana la" e evaziv

"Vrem sa va spunem ca exista o solutie..."
De ce e prost: pierde timpul cititorului; nu ofera valoare imediata; e generic

"Nu mai pierdeti timp si oportunitati..."
De ce e prost: cliseu agresiv; creeaza reactie de respingere; nu specifica beneficiul

---

INSTRUCTIUNI STRICTE:
1. Scrie EXCLUSIV in limba romana, FARA EMOJIS
2. Foloseste structura obligatorie de mai sus
3. Vorbeste la persoana a doua (TU), nu despre NOI
4. Fii specific, nu generic - evita fraze vagi
5. Include CTA clar si puternic
6. Fa continutul scanabil cu paragrafe scurte
7. Evita cuvinte de umplere si repetari inutile
8. Bazeaza-te pe principiile psihologice de mai sus

GENEREAZA CONTINUTUL ACUM:"""
        
        return prompt

    FRAMEWORKS: Dict[str, str] = {
        "AIDA": """AIDA Framework:
1. ATTENTION: Start with a powerful hook that grabs attention immediately
2. INTEREST: Build interest by highlighting the problem or opportunity
3. DESIRE: Create desire by showing benefits and transformation
4. ACTION: End with a strong, clear call-to-action""",
        
        "PAS": """PAS Framework:
1. PROBLEM: Clearly identify and agitate the pain point
2. AGITATE: Intensify the problem, make it feel urgent
3. SOLVE: Present your solution as the perfect answer""",
        
        "Benefit-Driven": """Benefit-Driven Framework:
- Lead with the main benefit, not features
- Use "so that" technique: Feature -> Benefit -> Ultimate result
- Focus on emotional and practical benefits
- Show transformation""",
        
        "Storytelling": """Storytelling Framework:
- Start with a relatable character/situation
- Present a conflict or challenge
- Show the journey/transformation
- End with resolution and lesson
- Make it emotional and authentic""",
        
        "Before-After-Bridge": """Before-After-Bridge Framework:
1. BEFORE: Describe the current painful situation
2. AFTER: Paint the picture of the ideal outcome
3. BRIDGE: Show how to get from Before to After""",
        
        "QUEST": """QUEST Framework:
1. Qualify: Address the right person
2. Understand: Show empathy for their situation
3. Educate: Provide valuable information
4. Stimulate: Create excitement/urgency
5. Transition: Move to call-to-action"""
    }

    CONTENT_TYPES: Dict[str, str] = {
        "Facebook Post": """STRUCTURA OBLIGATORIE pentru Facebook Post:

HOOK (primele 2 randuri - inainte de "Vezi mai mult"):
- O propozitie puternica care opreste scroll-ul
- Foloseste emotie, curiozitate sau contrarianism
- De ce: primele 2 randuri decid daca cititorul continua sau nu

CORPUL POSTARII:
- 3-5 paragrafe scurte cu linii goale intre ele
- Adreseaza direct pain point-ul audientei
- Include beneficii concrete, nu doar features
- Foloseste storytelling sau social proof
- FARA EMOJIS - par neprofesional in copy serios

CTA (Call-to-Action):
- O intrebare care provoaca comentarii SAU
- Un indemn clar sa dea like/share/save
- De ce: engagement-ul creste reach-ul organic

LUNGIME: 100-250 cuvinte
TON: Conversational, autentic, fara jargon

DE CE NU EMOJIS IN COPY SERIOS:
- Scad perceived value-ul ofertei
- Par infantil pentru audiente mature
- Distrag atentia de la mesajul principal""",
        
        "Instagram Caption": """STRUCTURĂ OBLIGATORIE pentru Instagram Caption:

**PRIMA LINIE (HOOK):**
- Text care captează atenția imediat
- Se vede în feed fără să apese "mai mult"

**CORPUL CAPTION-ULUI:**
- Mini-poveste sau valoare educativă
- Folosește bullet points pentru lizibilitate
- Include emojis strategice (3-5)
- Adaugă spacing pentru scanare ușoară

**CTA:**
- Îndeamnă să comenteze, salveze sau tag-uiască pe cineva

**HASHTAG-URI (15-30):**
#slabit #transformare #motivatie #sanatate #fitness #viatasanatoasa #antrenament #nutritie #bucuresti #romania #dezvoltarepersonala #succes #inspiratie #lifestyle #comunitate #pasiune #determinare #rezultate #schimbare #evolutie

**LUNGIME:** 100-220 cuvinte""",
        
        "Facebook Ad": """STRUCTURĂ OBLIGATORIE pentru Facebook Ad:

**PATTERN INTERRUPT (Headline):**
- O propoziție care sparge pattern-ul
- Ex: "STOP! Ai încercat 5 diete și nimic nu a funcționat?"

**PROBLEMĂ + AGITAȚIE:**
- Identifică problema clar
- Amplifică durerea/emotația (2-3 propoziții)

**SOLUȚIE + BENEFICII:**
- Prezenta soluția ca salvare
- 2-3 beneficii concrete cu rezultate

**SOCIAL PROOF:**
- Statistică, testimonial sau garanție

**CTA PUTERNIC:**
- Buton text clar: "Află mai mult", "Înscrie-te acum", "Obține oferta"
- Urgență sau scaritate (opțional)

**LUNGIME:** Sub 125 cuvinte (primary text)
**FOCUS:** Un singur beneficiu principal""",
        
        "Google Ad": """STRUCTURĂ OBLIGATORIE pentru Google Ad (Responsive Search Ad):

**HEADLINE 1 (max 30 caractere):**
[Keyword principal] + [Beneficiu principal]
Ex: "Slăbește 60 kg Garantat"

**HEADLINE 2 (max 30 caractere):**
[Differentiator] sau [Social proof]
Ex: "Metoda Verificată" sau "5000+ Clienți"

**HEADLINE 3 (max 30 caractere):**
[CTA clar]
Ex: "Începe Azi Gratuit"

**DESCRIERE 1 (max 90 caractere):**
[Value proposition detaliat]
Ex: "Scapă de kilograme fără diete drastice. Plan personalizat pentru tine."

**DESCRIERE 2 (max 90 caractere):**
[Urgency/CTA secundar]
Ex: "Ofertă limitată! Primești consultație gratuită la înscriere."

**FORMAT FINAL:**
Headline 1 | Headline 2 | Headline 3
Descriere 1
Descriere 2""",
        
        "Video Script": """STRUCTURĂ OBLIGATORIE pentru Video Script (60-90 secunde):

**SECUNDA 0-3 (HOOK):**
[Text pe ecran + voce]
- O propoziție care oprește scroll-ul imediat
- Ex: "Am slăbit 60 kg fără să renunț la mâncarea preferată"

**SECUNDA 3-15 (PROBLEMĂ):**
[Voce off + imagini relevante]
- Descrie problema audienței
- Agitează durerea ("Știi cum e să...")

**SECUNDA 15-45 (SOLUȚIE):**
[Demonstrație sau explicație]
- Prezenta soluția pas cu pas
- Arată beneficiile
- Include proof (rezultate, testimoniale)

**SECUNDA 45-60 (CTA):**
[Text pe ecran + voce clară]
- Îndemn puternic la acțiune
- Ex: "Link în bio pentru detalii" sau "Comentează 'DA' pentru mai multe info"

**NOTĂ:** Scrie pentru vorbit, nu pentru citit. Folosește propoziții scurte și cuvinte simple.""",
        
        "Email": """STRUCTURĂ OBLIGATORIE pentru Email:

**SUBIECT (max 50 caractere):**
- Curiosity gap sau benefit clar
- Evită spam words: "gratuit", "câștigă", "!!!"
- Ex: "Cum am slăbit 60 kg fără diete"

**PREVIEW TEXT (max 90 caractere):**
- Continuarea subiectului
- Adaugă context sau urgency

**SALUT:**
- Personalizat dacă e posibil
- Ex: "Bună [Nume]," sau "Salut,"

**PARAGRAF 1 - PROBLEMĂ:**
- Adresează pain point-ul direct
- Empatie și înțelegere

**PARAGRAF 2 - SOLUȚIE:**
- Prezenta soluția ta
- 2-3 beneficii principale

**PARAGRAF 3 - PROOF:**
- Rezultate, testimoniale, statistici

**CTA:**
- Un singur buton/link clar
- Text acțiune: "Află mai multe", "Înscrie-te acum"

**SIGN-OFF:**
- Profesional dar prietenos
- Include P.S. cu un mic hook (opțional)

**LUNGIME:** 150-300 cuvinte""",
        
        "Newsletter": """STRUCTURĂ OBLIGATORIE pentru Newsletter:

**SUBIECT + PREVIEW TEXT:**
- Subiect catchy + preview care completează

**HEADER:**
- Logo sau titlu newsletter
- Data/ediția

**SECȚIUNEA 1 - CONȚINUT PRINCIPAL (40%):**
- Articol sau tips valoros
- 2-3 paragrafe cu formatare
- Include imagine (recomandat)

**SECȚIUNEA 2 - NEWS/UPDATE (20%):**
- Știri scurte sau anunțuri
- Bullet points pentru scanare

**SECȚIUNEA 3 - OFERTĂ/CTA (30%):**
- Promoție sau produs recomandat
- Beneficii clare + CTA vizibil

**FOOTER:**
- Link-uri sociale
- Unsubscribe
- Contact info

**LUNGIME:** 500-800 cuvinte
**FORMATARE:** Headers, bullet points, bold pentru scanare rapidă""",
        
        "TikTok Script": """STRUCTURĂ OBLIGATORIE pentru TikTok Script (15-60 secunde):

**SECUNDA 0-1 (HOOK INSTANT):**
[Text pe ecran mare + expresie facială]
- Ex: "NU o să-ți vină să crezi!" sau "Secretul pe care nu ți-l spune nimeni"

**SECUNDA 1-5 (SETUP):**
[Voce rapidă, energică]
- Context rapid
- "POV: ai încercat tot să slăbești"

**SECUNDA 5-15 (REVELAȚIE):**
[Show, don't tell]
- Demonstrație sau tranziție
- Text on-screen cu puncte cheie

**SECUNDA 15-45 (CONȚINUT):**
[Fast-paced cuts]
- Tips sau steps rapide
- Trend sound (menționează în script)
- Engage cu camera

**SECUNDA 45-60 (CTA VIRAL):**
[Text pe ecran + gesturi]
- "Follow pentru partea 2"
- "Comentează 'DA' dacă vrei mai multe"
- "Save pentru mai târziu"

**TON:** Energetic, autentic, ca și cum vorbești cu un prieten
**LUNGIME:** 40-150 cuvinte""",
        
        "LinkedIn Post": """STRUCTURĂ OBLIGATORIE pentru LinkedIn Post:

**LINIA 1 (HOOK):**
- Insight, statistica sau început de poveste
- Ex: "Am dat 10.000€ pe cursuri de marketing. Iată ce-am învățat:"

**PARAGRAF 2-3 (DEZVOLTARE):**
- Povestea sau contextul
- Folosește linii goale pentru lizibilitate
- Fii vulnerabil/autentic

**PARAGRAF 4 (LEȚIE/INSIGHT):**
- Morala poveștii
- Un lesson practic
- Sau un framework simplu

**PARAGRAF 5 (CTA):**
- Întrebare care provoacă discuție
- Ex: "Tu ce experiență ai avut cu...?" sau "Care e cea mai mare provocare pentru tine?"

**HASHTAG-URI (3-5):**
#marketing #antreprenoriat #dezvoltarepersonala #business #succes

**LUNGIME:** 150-300 cuvinte
**TON:** Profesional dar personal, ca o conversație la cafea""",
        
        "Landing Page": """STRUCTURĂ OBLIGATORIE pentru Landing Page:

**HERO SECTION (Above the fold):**
- **Headline principal:** Benefit clar și specific
  Ex: "Slăbește 60 kg în 6 luni fără diete drastice"
- **Subheadline:** Suportă headline-ul cu context
- **CTA buton:** Text acțiune clar
- **Imagine/Video:** Rezultate sau demonstrație

**PROBLEMĂ + SOLUȚIE:**
- Identifică problema audienței
- Prezenta soluția ca unică opțiune viabilă

**BENEFICII (3-5):**
- Fiecare cu icon + titlu + descriere scurtă
- Focus pe outcomes, nu features

**SOCIAL PROOF:**
- Testimoniale cu nume, poză, rezultate
- Statistici: "5000+ clienți mulțumiți"
- Logouri branduri (dacă e cazul)

**CUM FUNCȚIONEAZĂ (3 pași):**
- Pasul 1: Înscriere/Consultație
- Pasul 2: Plan personalizat
- Pasul 3: Rezultate

**FAQ (3-5 întrebări):**
- Obiecții comune tratate direct

**CTA FINAL + URGENȚĂ:**
- Ofertă limitată sau bonus
- Formular simplu sau buton clar

**LUNGIME:** 1000-2000 cuvinte"""
    }

    @staticmethod
    def get_hashtags(category: str = "general") -> str:
        """Get relevant hashtags for Instagram posts."""
        hashtags = {
            "business": "#antreprenoriat #afaceri #succes #dezvoltarepersonala #motivatie #businessromania #antreprenor #leadership #productivitate #mindset",
            "fitness": "#fitness #sanatate #slabit #sport #nutritie #antrenament #motivatie #viatasanatoasa #gym #transformare",
            "lifestyle": "#lifestyle #viata #inspiratie #motivatie #fericire #bucuresti #romania #viatadem vis #pasiune #cresterpersonala",
            "marketing": "#marketing #vanzari #copywriting #digitalmarketing #socialmedia #contentmarketing #branding #promovare #onlinemarketing #strategie",
            "general": "#romania #bucuresti #viata #inspiratie #motivatie #dezvoltare #succes #pasiune #comunitate #share"
        }
        return hashtags.get(category, hashtags["general"])
