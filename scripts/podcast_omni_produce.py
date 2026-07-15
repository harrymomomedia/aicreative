import os, json, requests, pathlib, time, subprocess, re, sys, concurrent.futures
from dotenv import load_dotenv
load_dotenv("/Users/harry/aicreative/.env")
sys.path.insert(0, "/Users/harry/aicreative")
from elevenlabs_client import scribe_whisper_compat as scribe
TOKEN = os.environ["USEAPI_TOKEN"]; H = {"Authorization": f"Bearer {TOKEN}"}; EMAIL = "flowmomomedia@gmail.com"
# google-flow model: "omni-flash" (default) or "veo-3.1-lite-low-priority" (Ultra low-prio, free).
# Veo R2V allows referenceImage_1..3; duration must be 4/6/8 (dur_for already complies).
MODEL = os.environ.get("POD_MODEL", "omni-flash")
TAG = {"omni-flash": "", "veo-3.1-lite-low-priority": "_veo"}.get(MODEL, "_" + re.sub(r"[^a-z0-9]+", "", MODEL.split("-")[0]))
# Reference mode — USER-LOCKED 2026-07-15: ALWAYS startImage (I2V, literal first frame) for
# omni-flash too, not just Veo. R2V (referenceImage_1) re-stages framing per clip — on the DJI-mic
# selfie format the arm/POV came out different clip to clip (W_Z1). startImage pins the anchor as
# frame 1 of every clip: identical framing + background hold. Override with POD_REF=referenceImage_1
# if a run ever needs the old loose-reference behavior.
IS_VEO = MODEL.startswith("veo")
REF_PARAM = os.environ.get("POD_REF", "startImage")
ROOT = pathlib.Path("/Users/harry/aicreative/outputs/chowchilla_podcast")
BR = pathlib.Path("/Users/harry/aicreative/outputs/chowchilla_podcast_bright")
MD = pathlib.Path("/Users/harry/aicreative/outputs/chowchilla_podcast_personas")  # moody set

PERSONAS = {"B1":BR/"1.png","B2":BR/"2.png","B3":BR/"3.png","B4":BR/"4.png","B5":BR/"5.png","B6":BR/"6.png","B9":BR/"9.png",
            "M8":MD/"8.png",
            "Q6":MD/"Q6.png",  # rugged ex-inmate Black woman mid-40s, flannel + white tee, iPhone-video look (bright)
            "Z1":MD/"Z1.png",  # Chicana ~48, DJI-mic selfie, sidewalk, fired up      (W)
            "Z2":MD/"Z2.png",  # Latina ~52, DJI-mic selfie, living-room window, tense (X)
            "Z4":MD/"Z4.png",  # Black ~50, DJI-mic selfie, front stoop, angry         (U)
            "Z6":MD/"Z6.png",  # Black ~47, DJI-mic selfie, kitchen, excited           (V)
            "V6":pathlib.Path("/Users/harry/aicreative/outputs/cawp_r11_pattern/reference/v6_rooftop.png"),
            "SB1":pathlib.Path("/Users/harry/aicreative/outputs/cawp_r11_pattern/reference/s1b_storage.png"),
            "SB2":pathlib.Path("/Users/harry/aicreative/outputs/cawp_r11_pattern/reference/s2b_greenhouse.png"),
            "SB3":pathlib.Path("/Users/harry/aicreative/outputs/cawp_r11_pattern/reference/s3b_mural.png"),
            "SB4":pathlib.Path("/Users/harry/aicreative/outputs/cawp_r11_pattern/reference/s4b_poppies.png"),
            "SB5":pathlib.Path("/Users/harry/aicreative/outputs/cawp_r11_pattern/reference/s5b_drivein.png"),
            "SB6":pathlib.Path("/Users/harry/aicreative/outputs/cawp_r11_pattern/reference/s6b_agave.png"),
            "SB7":pathlib.Path("/Users/harry/aicreative/outputs/cawp_r11_pattern/reference/s7b_lakebed.png")}  # R11 DJI-mic yapper set  # moody #8 — weathered, headphones, condenser mic, dark cardigan, low-key light

# letter: (persona, tone, vernacular_text)
SCRIPTS = {
 "A": ("B6","fired up, urgent, real grown-woman conviction",
   "Real talk. If a guard or an officer sexually abused you in a California women's prison, I need you to hear me. Whether it was Chowchilla, CCWF, or CIW, you may qualify for significant potential compensation. Survivors from another California women's prison already won over a hundred million dollars. You don't need paperwork, you don't need proof, none of that. Most of these get handled without you ever stepping foot in a courtroom. You only pay if you win. It all stay private, just between you and the lawyers. Don't sleep on what could be yours. Tap that button and see if you qualify."),
 "B": ("B2","earnest, building conviction, like she's putting you on to something",
   "This is how women who was sexually abused in the California prisons may qualify for significant potential compensation. I know it sound wild. Stay with me. Survivors from another California women's prison just won over a hundred and sixteen million dollars. If you was sexually abused by a guard or an officer while you was locked up in Chowchilla, you may qualify too. Even if it happened years ago. Even if you never told a soul. Even if you never reported it. Tap that button and take the quiz to see if you qualify. It's free, and it's private."),
 "D": ("B1","authoritative but warm, urgent",
   "Attention. If you was sexually abused by a guard or an officer while you was locked up in a California women's prison, you need to hear this. Whether it was Chowchilla, CCWF, or CIW, the law is on your side now. You may qualify for significant potential compensation. This ain't no scam. Survivors from another California women's prison already won over a hundred and sixteen million dollars. Cases is being reviewed right now. You don't need a old report. You don't need your own lawyer. You don't even gotta set foot in a courtroom. And you pay nothing unless they win for you. Everything stay private, just between you and the attorneys. Take one minute. Tap that button and find out if you qualify."),
 "F": ("B3","righteous anger, fierce, fired up",
   "Those guards in Chowchilla was betting on one thing. That after they sexually abused us, we would be too ashamed to ever open our mouths. That we would carry it straight to our graves. They bet wrong. Women who was sexually abused inside the California prisons may qualify for significant potential compensation now. Survivors from another women's prison out here already won over a hundred million dollars for it. You don't need proof, or a old report, or none of that. The courts is finally making these places answer. You only pay if you win. It all stay private, just between you and the lawyers. After everything they took, this part is yours. Tap that button and see if you qualify."),
 "H": ("B4","warm, targeted, building intensity",
   "This is for you if a guard or an officer sexually abused you in a California women's prison. This is for you if it was Chowchilla, CCWF, or CIW. This is for you if you told yourself it wasn't that bad, or it was too long ago to matter. It was that bad, and it still matter. You may qualify for significant potential compensation. Survivors from another California women's prison already won over a hundred million dollars. You don't need proof, you don't need a report, and you don't gotta go to court. You don't pay unless they win. It stay private, just you and the lawyers. If any of this is landing for you, it ain't a coincidence. Tap that button and see if you qualify."),
 "I": ("B9","heavy, confronting, intimate, fired up",
   "If a guard ever came in your cell at night when you was locked up in Chowchilla, don't scroll past this. What he did to you was sexual abuse, even if you never once called it that. Women who lived through it in the California prisons may qualify for significant potential compensation. Survivors from another women's prison out here already won over a hundred million dollars. You don't need no proof, no old report, nothing like that. You only pay if you win. You don't even gotta go to court. It stay private, just between you and the lawyers, no matter how many years it's been. Take a minute. Tap the button. See if you qualify."),
 "M": ("B5","tender naming it plainly, then urgent",
   "What that guard did to you in prison has a name. It was sexual abuse. And if it happened to you inside Chowchilla, or any California women's prison, you may qualify for significant potential compensation. Survivors from another California women's prison already won over a hundred and sixteen million dollars. Cases like yours is being reviewed right now. You don't need proof. You don't need a report. You don't gotta set foot in court. You only pay if you win. Nobody gotta know but you and the lawyers. It don't matter how many years gone by. Take one minute, tap that button, and see if you qualify."),
 "P": ("V6","calm, serious, compassionate; quiet conviction on the evidence lines; settles softly at the end",
   "A woman I did time with asked me, how can anyone prove what happened inside C-I-W years ago? I asked the same thing when I filed. Because I thought it was my word against his. When you've been sexually abused inside, your biggest fear is that nobody's going to believe you. For years I told myself, who's going to listen to an incarcerated woman? So I stayed quiet. Here's what I found out. The lawyers don't just take one story. They find out who else was there. Same facility. Same years. Same staff. They look for the echoes. And a pattern showed up. I remembered a hallway. Another woman I never met described the same hallway. A third woman named the same officer. A fourth described the same threat he used on us. It stopped being my word against his. One story gets dismissed. Ten women saying the same thing, that's evidence. That's a pattern of abuse. The kind the institution was supposed to stop. So how do you prove what happened all those years ago? Together. That's how. If this is your story, the form below is private and confidential. You may qualify for significant potential compensation."),
 "Q": ("Q6","steady straight talk, quiet conviction; low controlled anger on the institution lines; settles soft and private at the end",
   "If you was locked up at Chowchilla, Valley State, or C-I-W, stop scrolling. This is for you. A woman I was inside with asked me something real. Do I have to face him in court? The answer is no, and I need you to hear why. That same fear kept me quiet too. If a guard or an officer sexually abused you in there, the claim is against the institution, not against him. The state was supposed to keep us safe. The claim makes the institution answer for what it let happen. That means no confrontation. You don't sit across from him. You don't need him to admit nothing. Most of it is records and paperwork. It's handled private, step by step, by people who believe you. Nobody in your life gotta know. Not your family, not your job. It stays completely confidential. You may qualify for significant potential compensation. It's free to check. Tap the button and see if you qualify."),
 "S1": ('SB1','steady, knowing, like passing on hard-won knowledge; softens at the end',
   "I did time in a California women's prison. And I've spent the last year helping other women file claims for the sexual abuse that happened inside. Here's what I learned that the system doesn't want you to know. First. What happened to us wasn't rare. The same facilities, the same officers, the same stories, over and over. Second. Almost nobody reported it back then. Because inside, reporting it got YOU punished. The lawyers know that now. Not reporting doesn't disqualify you. And these claims may mean significant potential compensation, even all these years later. Third. The women who stayed quiet the longest are the ones who qualify most often. Twenty years of silence doesn't close the door. If a guard or staff member sexually abused you inside, there's a private form. A few questions, between you and the lawyers. Take the two minutes."),
 "S2": ('SB2','gentle, serious, carrying weight; quiet relief near the end',
   "A woman I know carried what happened to her at C-I-W for fifteen years. She figured nothing could ever be done about it. A guard sexually abused her, and she told herself that door closed a long time ago. Then she found out one thing. California changed the law. Women like her can file claims now, even for things that happened years ago. And those claims may mean significant potential compensation. She sat with that for a week. Then she filled out the form. Took her a few minutes. Everything stayed private, between her and the lawyers. Fifteen years of thinking it was too late, and it wasn't. If you were sexually abused inside a California women's prison, it's not too late for you either. Tap the button. Check for yourself."),
 "S3": ('SB3','firm, direct, myth-busting conviction, a little fed up on each WRONG',
   "I just got off the phone with a woman who almost let this pass her by. She was sexually abused inside, and she believed three things that are not true. Myth one. Nobody believes an incarcerated woman. Wrong. These cases get built from patterns. Dozens of women describing the same officers, the same spots, the same threats. Myth two. It's been too long. Wrong. California opened the door for claims from years back. What happened to her was sexual abuse, and she may qualify for significant potential compensation because of it. Myth three. She'd have to stand in a courtroom and face him. Wrong again. The claim is against the institution that let it happen. Most women never see a courtroom at all. She filled out the form. Private, just her and the lawyers. If staff sexually abused you inside, don't let the myths decide for you. Check for yourself."),
 "S4": ('SB4',"close and personal, telling a friend's story; warm resolve at the end",
   "I want to tell you about a conversation I had with a woman I was locked up with. She was sure nobody would ever believe her story. A guard sexually abused her inside, and she'd never said it out loud. Not once. What she didn't know is that hundreds of women from that same facility were already filing claims. Claims that may qualify them for significant potential compensation. Women she walked the yard with. Women she never met. All telling stories that matched hers. She wasn't alone. She was never alone. She just couldn't see the others. When she found that out, everything changed. She filled out the form that same night. If you were sexually abused at a California women's prison, you're not the only one. The form's below. It's private."),
 "S5": ('SB5','matter-of-fact, quietly angry, hard-earned truth; steady close',
   "Somebody asked me, what's the most common reason women from places like Chowchilla never come forward about the sexual abuse inside? It's not what you think. It's not shame. It's training. Inside, we learned that telling made things worse. You report it, you get written up. You get moved. You get your parole date played with. The system taught us that silence was the only safe move. But that's exactly why the law changed. California opened the door for women like us to file claims now, and those claims may mean significant potential compensation. Even for things that happened way back. If a guard or staff member sexually abused you inside, staying quiet doesn't have to be the plan anymore. One private form. You and the lawyers. Check where you stand."),
 "S6": ('SB6','proud, warm grit, honoring the women; firm loving push at the end',
   "Since I came home, I've talked with about fifty women who did time at C-I-W or Chowchilla. Women who went through sexual abuse inside, like I did. And here's the biggest lesson they taught me. It never broke them. They raised kids. They held down jobs. They carried the whole thing in silence and kept everybody standing. But strength shouldn't mean carrying it for free. These women are checking their claims now, and a lot of them may qualify for significant potential compensation. Quietly. Privately. Between them and the lawyers, nobody else. That's not weakness. That's finally putting it down. If you're one of us, take the two minutes. You carried enough already. Tap the button and see where you stand."),
 "S7": ('SB7','dry, plainspoken, counting it off; direct close',
   "I've helped a lot of women get their claims looked at this past year. Claims for sexual abuse inside the California prisons. Women like me. Three things surprised me. One. How much the stories overlap. Different women, different years, same officers, same buildings. You realize it was never just you. And that overlap is exactly why these claims may qualify for significant potential compensation. Two. How many women never told a single soul. Husbands of thirty years who still don't know. And that's fine. The form is private. Nobody in your life has to be part of it. Three. How fast checking is compared to how long we waited. Women sat on this for twenty years, and the check took them two minutes. If a guard or staff member sexually abused you inside, that's all it takes to find out. The button's right there."),
 "U": ("Z4","controlled righteous anger, hard and direct, heat builds on the institution lines, lands firm at the end",
   "Somebody asked me, if the claim is against the institution, does he just get away with it? She meant the staff who sexually abused women inside California women's prisons. The answer is no, so hear me out. A claim like this puts what he did on the record. With your name protected. It makes the system that let him operate finally answer for it. Guards like him counted on silence. Every claim filed breaks that. If it happened to you at Chowchilla, Valley State, or C-I-W, you don't gotta carry it quiet. You may qualify for significant potential compensation. Checking is free and private. Tap the button below and make it count."),
 "V": ("Z6","excited, animated, putting-you-on energy, warm and reassuring through the walkthrough, bright at the end",
   "A woman asked me, what actually happens after I send in the form? She was sexually abused by staff at C-I-W, and she was nervous. I get it. So let me walk you through it. The form takes about two minutes. Facility, years, what happened, that's it. Then somebody from the legal team calls you. Private number, just you and them. It's a conversation, not an interrogation. You share what you're comfortable sharing. Nobody shows up at your door. Nothing goes public. Your people don't find out. That goes for Chowchilla, Valley State, and C-I-W women all the same. You may qualify for significant potential compensation. No cost either way. The form is below, two minutes, whenever you ready."),
 "W": ("Z1","fired up, emphatic, myth-busting street straight talk, punchy and certain",
   "So many women think the problem is they can't afford a lawyer to fight. I mean women sexually abused by staff at Chowchilla, Valley State, or C-I-W. I thought the same. Real lawyers cost real money I did not have. Here's what nobody told us. These cases don't work like that. The law firm only gets paid if you win. That's the whole deal. No retainer, no hourly bill, no out-of-pocket, nothing up front. They only take your case if they believe in it. So they fight to win it. Money is not the reason to stay quiet, not anymore. You may qualify for significant potential compensation. Checking costs you nothing. Tap below, two minutes, zero dollars."),
 "X": ("Z2","urgent and shaken, just witnessed it, tense energy that softens into moved relief at the end",
   "I just watched somebody put down a fear she carried for twenty years. One phone call. And one line in this new California law. My friend was sexually abused by a guard at Chowchilla. The law basically says it's not too late. Old cases still count. Twenty years she thought her window was closed. It never was. She hung up the phone different, lighter, like somebody finally heard her. If that's you, from Chowchilla, Valley State, or C-I-W, your window is open too. You may qualify for significant potential compensation. It's free, it's confidential, and it starts with one private form. Tap below and put it down like she did."),
 "K": ("M8","intimate, warm, sister-to-sister, then fired up",
   "Sis, listen. If a guard or an officer sexually abused you while you was locked up in a California women's prison, this is for you. Chowchilla, CCWF, CIW, it don't matter which one. What he did to you was sexual abuse, even if you never once called it that. And you may qualify for significant potential compensation. Survivors from another California women's prison already won over a hundred and sixteen million dollars. You don't need proof. You don't need a old report. You don't even gotta step foot in a courtroom. You only pay if you win. And it stay private, just between you and the lawyers. Don't let them win twice. Tap that button and see if you qualify."),
}

# Veo i2v is 8s-flat and drags on tiny lines, so the omni short-chunk strategy doesn't transfer.
# For Veo, group each script into fuller ~13-22-word beats (6s if <=14 words, else 8s) so every
# clip is well-filled at ~2.2-2.6 words/sec. Curated per letter for clean beat boundaries.
VEO_CHUNKS = {
 "K": [
   "Sis, listen. If a guard or an officer sexually abused you while you was locked up in a California women's prison",
   "This is for you. Chowchilla, CCWF, CIW, it don't matter which one",
   "What he did to you was sexual abuse, even if you never once called it that",
   "And you may qualify for significant potential compensation. Survivors from another California women's prison already won over a hundred and sixteen million dollars",
   "You don't need proof. You don't need a old report. You don't even gotta step foot in a courtroom",
   "You only pay if you win. And it stay private, just between you and the lawyers",
   "Don't let them win twice. Tap that button and see if you qualify",
 ],
}

def chunk_for(letter, text):
    if IS_VEO and letter in VEO_CHUNKS: return VEO_CHUNKS[letter]
    return chunk(text)

GAZE = "GAZE LOCK: she looks DIRECTLY into the camera lens the ENTIRE clip, steady, never drifting off to the side."
BODY = ("She stays seated in place and speaks into the podcast microphone with natural expressive life: alive "
        "eyes and brows, small hand gestures, nods, blinks. She does NOT lunge at the camera and does NOT sway. No smile.")
BG = ("BACKGROUND LOCK: keep the EXACT SAME background, room, wall, and lighting as in the reference image. "
      "Do NOT change, swap, or re-imagine the background — reproduce the identical setting from the reference "
      "in every shot, unchanging across the whole clip. Same place, same background, same framing the entire time.")

LETTER = None
VOICE_DEFAULT = ("a weathered late-40s Black woman from South Central Los Angeles, low, raspy, fired up, real LA "
        "vernacular, NOT flat, NOT an announcer")
VOICES = {"P": ("a worn Southern California Latina woman in her early fifties, steady, low, calm and serious, "
        "plain everyday talk, NOT flat, NOT an announcer"),
          "Q": ("a weathered mid-40s Black woman who has lived hard, low and steady, plain straight talk, "
        "lived-in and real, quiet conviction, NOT flat, NOT an announcer"),
 "S1": "a worn LA Latina woman in her fifties, steady low voice, plain real talk, knowing and direct, NOT an announcer. PRONUNCIATION: the word 'guard' is pronounced GARD, hard American G, one syllable, never gward",
 "S2": "a tired warm LA Latina woman in her late fifties, soft low voice, gentle and serious, NOT an announcer. PRONUNCIATION: the word 'guard' is pronounced GARD, hard American G, one syllable, never gward",
 "S3": "a working-class LA Latina woman in her late forties, firm clear voice, direct, a little fed up, NOT an announcer. PRONUNCIATION: the word 'guard' is pronounced GARD, hard American G, one syllable, never gward",
 "S4": "a worn LA Latina woman in her fifties, low warm voice, close and personal like telling a friend, NOT an announcer. PRONUNCIATION: the word 'guard' is pronounced GARD, hard American G, one syllable, never gward",
 "S5": "a hard-lived LA Latina woman in her mid fifties, flat low gravelly voice, matter-of-fact, quietly angry, NOT an announcer. PRONUNCIATION: the word 'guard' is pronounced GARD, hard American G, one syllable, never gward",
 "S6": "a sturdy LA Latina woman in her early fifties, warm low voice with grit, proud and serious, NOT an announcer. PRONUNCIATION: the word 'guard' is pronounced GARD, hard American G, one syllable, never gward",
 "S7": "a wiry LA Latina woman in her late forties, dry steady voice, plainspoken, NOT an announcer. PRONUNCIATION: the word 'guard' is pronounced GARD, hard American G, one syllable, never gward",
 "U": ("a weathered Black woman about fifty, low, firm, controlled anger that builds, "
        "plain straight talk, NOT flat, NOT an announcer"),
 "V": ("a weathered Black woman in her late forties, warm, bright, animated and energized, "
        "plain everyday talk, NOT flat, NOT an announcer"),
 "W": ("a weathered Chicana Latina woman in her late forties from Southern California, low, "
        "strong, emphatic, fired up, plain everyday talk, NOT flat, NOT an announcer"),
 "X": ("a worn Southern California Latina woman in her early fifties, urgent, low, emotionally "
        "charged, a little shaken, plain everyday talk, NOT flat, NOT an announcer")}
_STAND = "standing and holding the small wireless mic at chest height, speaking over it"
POSTURES = {"P": _STAND, "S1": _STAND, "S2": _STAND, "S3": _STAND, "S4": _STAND, "S5": _STAND, "S6": _STAND, "S7": _STAND,
            # U/V/W/X (DJI-selfie set): NO object/scene nouns — the anchor carries all visuals;
            # posture just pins her in place. ("holding the mic" etc. re-described the anchor.)
            "U": "in place exactly as in the reference image, standing STILL, NOT walking",
            "V": "in place exactly as in the reference image, standing STILL, NOT walking",
            "W": "in place exactly as in the reference image, standing STILL, NOT walking",
            "X": "in place exactly as in the reference image, standing STILL, NOT walking"}
# per-letter EXTRA background locks — ABSTRACT only (user-locked 2026-07-15: prompt = stability
# behavior + performance, zero named objects). If a future run's background drifts anyway, the
# escalation is a TARGETED negative lock naming the in-anchor element ("cars stay parked" held
# W's street) — but the default stays noun-free.
_STILL = "Nothing in the background moves at all; everything behind her stays completely still. "
EXTRA = {"U": _STILL, "V": _STILL, "W": _STILL, "X": _STILL}

def build(dia, tone, letter=None):
    posture = POSTURES.get(letter, "seated")
    voice = VOICES.get(letter, VOICE_DEFAULT)
    # NO visual object nouns in this boilerplate (user-locked 2026-07-15): omni literalizes prompt
    # nouns — "locked-off TRIPOD" spawned actual tripods mid-clip (V/X), same class as the
    # headphones lesson. Camera/scene direction must be abstract; the reference image carries
    # ALL visuals. Negative locks in EXTRA ("no passing cars") are fine — positives are not.
    return ("Vertical close-up, framed IDENTICALLY from the first frame to the last. The framing is "
        "completely locked: no reframing, no settling, no drift, no zoom, no pan. The background stays "
        "EXACTLY as in the reference image, frozen, never moving or changing; only her face and hands "
        "move. "+EXTRA.get(letter,"")+"She stays "+posture+" and speaks with natural expressive life: alive eyes "
        "and brows, small hand gestures, nods, blinks, no smile, does not lunge. She looks straight into the lens. "
        "VOICE: "+voice+". TONE: "+tone+". Brisk delivery, about 2.4 words per second, no "
        "long pauses. She says ONLY this, verbatim, no extra or repeated words, then stops: \""+dia+"\" No on-screen text, no music.")

def chunk(text):
    parts = re.split(r'(?<=[.?!])\s+', text.strip()); out=[]
    for p in parts:
        p=p.strip().rstrip('.?!').strip()
        if not p: continue
        if len(p.split())<=13: out.append(p); continue
        # pack comma-clauses into <=13-word groups (don't isolate tiny fragments)
        cur=[]
        for c in re.split(r',\s*', p):
            c=c.strip()
            if not c: continue
            if len((" ".join(cur+[c])).split())<=13: cur.append(c)
            else:
                if cur: out.append(", ".join(cur))
                cur=[c]
        if cur: out.append(", ".join(cur))
    return out

def dur_for(dia):
    w=len(dia.split())
    if IS_VEO:
        return 6 if w<=14 else 8        # Veo i2v drags on tiny lines; no 4s (guardrail-prone). 6 or 8 only.
    return 4 if w<=6 else (6 if w<=10 else 8)

def split_dia(dia):
    ws=dia.split()
    if ',' in dia:
        i=dia.find(','); return dia[:i].strip(), dia[i+1:].strip()
    mid=len(ws)//2; return " ".join(ws[:mid]), " ".join(ws[mid:])

NUMCORE=set("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million billion trillion".split())
NUMGLUE={"a","and","point","oh"}
NUMCUR={"dollar","dollars","cent","cents","buck","bucks","grand","percent"}

def _prep(text, intended=False):
    # Returns (words, hyset). Canonicalizes a transcript/line into comparable word tokens:
    #  - strips podcast reaction tokens (mm-hmm / mm-mm / uh-huh / ah-ah / hm-mm ... any nasal/vowel
    #    chain joined by hyphen/space) — never a real word, always trailing improv the trim removes;
    #  - folds benign colloquial variants Veo/Scribe swap ("got to"<->"gotta", "going to"<->"gonna",
    #    "want to"<->"wanna", "an"->"a") so they don't read as missing/extra words;
    #  - folds any NUMBER phrase ("a hundred and sixteen million dollars" / "$116 million" / "116
    #    million") to a single "#num#" token — Scribe renders spoken amounts as digits, which would
    #    otherwise break the subsequence match (clip-03 "$116 million" false-"missing").
    # hyset = word-indices whose source token carried a hyphen (false-start candidate, e.g. "pr-").
    # Strip reaction chains (mm-hmm / uh-huh / ah-ah) — ENUMERATED tokens only. The old class
    # [mhaeiouy]+ chain regex ate REAL words: "You may" (you=vowels, may=m+vowels) was stripped
    # from the INTENDED line, so the trimmer deterministically started at "qualify" — the root
    # cause of the Q-18a / W-12 / U-11 "You may" losses (NOT Scribe nulls). 2026-07-15.
    _R=r"(?:m+|h+m+|m+h+m*|u+h+|h+u+h*|a+h+|a+h*a+|o+h+)"
    text=re.sub(r"\b"+_R+r"(?:[-\s]+"+_R+r")+\b"," ",text,flags=re.I)
    t=text.lower()
    if intended:
        # dehyphenate SCRIPT compounds (out-of-pocket) — scripts have no false-starts, so this is
        # safe on the intended side (Scribe renders them unhyphenated -> false "missing", W-08 leak).
        # ONLY between multi-letter words: letter-spellings like "C-I-W" must STAY joined so they
        # canonicalize to "ciw" and match Scribe's "CIW" (splitting them cost U-09 3 takes, 2026-07).
        t=re.sub(r"(?<=[a-z]{2})-(?=[a-z]{2})"," ",t)
    t=re.sub(r"\bup front\b","upfront",t)   # fold compound to ONE canonical token on BOTH sides
    t=re.sub(r"\bgot to\b","gotta",t); t=re.sub(r"\bgoing to\b","gonna",t)
    t=re.sub(r"\bwant to\b","wanna",t); t=re.sub(r"\ban\b","a",t)
    toks=re.findall(r"[a-z'\-]+|\d[\d,\.]*",t)
    cw=[re.sub(r"[^a-z']","",x) for x in toks]
    member=[bool(re.match(r"\d",toks[k])) or cw[k] in NUMCORE for k in range(len(toks))]
    chg=True                                              # grow runs over adjacent glue/currency
    while chg:
        chg=False
        for k in range(len(toks)):
            if member[k] or not cw[k]: continue
            if cw[k] in NUMGLUE or cw[k] in NUMCUR:
                if (k>0 and member[k-1]) or (k+1<len(toks) and member[k+1]):
                    member[k]=True; chg=True
    words=[]; hyset=set(); k=0
    while k<len(toks):
        if member[k]:
            while k+1<len(toks) and member[k+1]: k+=1
            words.append("#num#"); k+=1; continue
        if cw[k]:
            if "-" in toks[k]: hyset.add(len(words))
            words.append(cw[k])
        k+=1
    return words,hyset

def _prep_ts(ws):
    # Canonicalize a Scribe word list (each {word,start,end}) the SAME way as _prep, but KEEP
    # timestamps, so jumpcut can trim to the intended span even when Scribe renders the amount as
    # digits ("$116 million") or swaps got-to/gotta, an/a. Returns (canon_words, starts, ends),
    # number-runs folded to a single "#num#" spanning [first start, last end].
    items=[]; i=0; n=len(ws)
    while i<n:
        raww=(ws[i].get("word") or "").strip(); s=ws[i].get("start"); e=ws[i].get("end")
        if re.fullmatch(r"[mhaeiouy]+(?:[-\s][mhaeiouy]+)+", raww, flags=re.I):
            i+=1; continue                                       # podcast reaction token -> drop
        if re.search(r"\d", raww):
            items.append(("#d#", s, e)); i+=1; continue          # digit -> number-core placeholder
        cw=re.sub(r"[^a-z']","",raww.lower())
        nxt=re.sub(r"[^a-z']","",(ws[i+1].get("word") or "").lower()) if i+1<n else ""
        if cw in ("got","going","want") and nxt=="to":
            items.append(({"got":"gotta","going":"gonna","want":"wanna"}[cw], s, ws[i+1].get("end"))); i+=2; continue
        if cw=="an": cw="a"
        if cw: items.append((cw,s,e))
        i+=1
    member=[(it[0]=="#d#" or it[0] in NUMCORE) for it in items]
    chg=True
    while chg:
        chg=False
        for k in range(len(items)):
            if member[k] or not items[k][0]: continue
            if items[k][0] in NUMGLUE or items[k][0] in NUMCUR:
                if (k>0 and member[k-1]) or (k+1<len(items) and member[k+1]):
                    member[k]=True; chg=True
    words=[]; starts=[]; ends=[]; k=0
    while k<len(items):
        if member[k]:
            j=k
            while j+1<len(items) and member[j+1]: j+=1
            words.append("#num#"); starts.append(items[k][1]); ends.append(items[j][2]); k=j+1; continue
        words.append(items[k][0]); starts.append(items[k][1]); ends.append(items[k][2]); k+=1
    return words,starts,ends

def clean(text, dia):
    # Trailing/leading improv is NOT rejected here — the jump-cut assembler trims to the
    # intended span via Scribe word-timestamps, so paying to re-roll it is pure waste.
    # Reject ONLY defects that survive the trim: the line not fully spoken (missing), a false-start
    # fragment BETWEEN intended words ("pr- prove"), or a stutter inside the kept span.
    # Scribe renders compounds inconsistently ("out-of-pocket" vs "out of pocket"). Dehyphenate a
    # transcript compound ONLY when every part is a word of the intended line — a real false-start
    # ("insti-institution") has a fragment part that is NOT an intended word, so it stays hyphenated
    # and the hyset check still catches it.
    _iw=set(re.findall(r"[a-z']+", dia.lower().replace("-"," ")))
    def _dehy(mo):
        parts=[p for p in mo.group(0).lower().split("-") if p]
        return " ".join(parts) if len(parts)>1 and all(p in _iw for p in parts) else mo.group(0)
    text=re.sub(r"[A-Za-z']+(?:-[A-Za-z']+)+", _dehy, text)
    w,hy=_prep(text)
    intended,_=_prep(dia, intended=True)
    intset=set(intended)
    wi=0; first=None; last=None                           # ordered subsequence match -> kept span
    for j,tok in enumerate(w):
        if wi<len(intended) and tok==intended[wi]:
            if first is None: first=j
            last=j; wi+=1
    if wi<len(intended): return False,"missing"           # whole line not spoken -> re-roll
    for j in hy:                                          # false-start ONLY if interior AND not a
        if first<j<last and w[j] not in intset:           # complete scripted word (lets "C-C-W-F"
            return False,"hyphen"                          # letter-spelling pass; trailing cutoffs trimmed)
    span=w[first:last+1]                                  # exactly what survives the trim
    for n in (1,2,3):                                     # mid-line stutter in kept span
        for i in range(len(span)-2*n+1):
            if span[i:i+n]==span[i+n:i+2*n]:
                dbl=span[i:i+2*n]                          # script-intrinsic repeat (e.g. "step by
                if any(intended[k:k+2*n]==dbl              # step, by") is INTENDED text, not a
                       for k in range(len(intended)-2*n+1)):  # stutter -> don't reject (14b leak,
                    continue                               # 2026-07: correct takes rejected 2x)
                return False,f"{n}gram"
    return True,"ok"

def upload(path, ctype="image/png"):
    with open(path,"rb") as f:
        r=requests.post(f"https://api.useapi.net/v1/google-flow/assets/{requests.utils.quote(EMAIL)}",headers={**H,"Content-Type":ctype},data=f.read(),timeout=180)
    m=r.json().get("mediaGenerationId"); return m.get("mediaGenerationId") if isinstance(m,dict) else m

def gen(out, dia, dur, mgid, tone, attempts=3):
    if out.exists() and out.stat().st_size>50000: return True
    for a in range(1,attempts+1):
        payload={"prompt":build(dia,tone,LETTER),"model":MODEL,"aspectRatio":"portrait","duration":dur,
                 "count":1,"captchaRetry":3,"seed":(abs(hash(out.name))%9000)+a*31}
        payload[REF_PARAM]=mgid
        try:
            g=requests.post("https://api.useapi.net/v1/google-flow/videos",headers={**H,"Content-Type":"application/json"},json=payload,timeout=600)
            gj=g.json()
            if g.status_code==200 and gj.get("media"):
                tmp=f"/tmp/_p_{out.stem}.mp4"; open(tmp,"wb").write(requests.get(gj["media"][0]["videoUrl"],timeout=180).content)
                subprocess.run(["ffmpeg","-y","-i",tmp,"-vn","-ar","16000","-ac","1",f"/tmp/_p_{out.stem}.wav"],capture_output=True)
                txt=scribe(f"/tmp/_p_{out.stem}.wav",biased_keywords=["Chowchilla","CCWF","CIW"],language_code="en").get("text","")
                ok,why=clean(txt,dia)
                if ok:
                    open(out,"wb").write(open(tmp,"rb").read())
                    # per-clip MODE RECEIPT from Google's own record (settles i2v-vs-r2v questions)
                    _md=(gj.get("media") or [{}])[0]
                    _gv=(_md.get("video") or {}).get("generatedVideo",{})
                    _vm=(_md.get("mediaMetadata",{}).get("requestData",{}).get("videoGenerationRequestData",{})
                         .get("videoModelControlInput",{}))
                    print(f"  {out.name} CLEAN a{a}  [mode: {_gv.get('model') or _vm.get('videoModelName')} / {_vm.get('videoGenerationMode','?')}]",flush=True)
                    return True
                print(f"  {out.name} a{a} REJECT[{why}]  txt={txt!r}",flush=True)
            else:
                try: rs=gj["response"]["media"][0]["mediaMetadata"]["mediaStatus"].get("failureReasons")
                except Exception: rs=str(gj.get("error") or gj)[:70]
                print(f"  {out.name} a{a} GENFAIL {rs}",flush=True)
        except Exception as e: print(f"  {out.name} a{a} EXC {str(e)[:70]}",flush=True)
        time.sleep(6)
    return False

def do_chunk(args):
    i,dia,mgid,tone=args
    base=DIR/f"{i:02d}.mp4"; a_=DIR/f"{i:02d}a.mp4"; b_=DIR/f"{i:02d}b.mp4"
    if base.exists() and base.stat().st_size>50000: return
    if a_.exists() and b_.exists(): return
    if gen(base,dia,dur_for(dia),mgid,tone,attempts=3): return
    if IS_VEO or len(dia.split())<=6:
        # Veo chunks are already fuller beats — splitting makes draggy fragments. Just drop on fail.
        print(f"  !! {i:02d} clip won't clear after retries, NOT splitting (dropping): '{dia}'",flush=True); return
    d1,d2=split_dia(dia)
    print(f"  >> splitting {i:02d}: '{d1}' | '{d2}'",flush=True)
    gen(a_,d1,dur_for(d1),mgid,tone,attempts=2); gen(b_,d2,dur_for(d2),mgid,tone,attempts=2)

def jumpcut(files, dias, out):
    trimmed=[]
    for j,fn in enumerate(files):
        p=DIR/fn; wav=f"/tmp/_jc_{p.stem}.wav"
        subprocess.run(["ffmpeg","-y","-i",str(p),"-vn","-ar","16000","-ac","1",wav],capture_output=True)
        ws=[w for w in scribe(wav,biased_keywords=["Chowchilla"],language_code="en").get("segments",[{}])[0].get("words",[]) if w.get("start") is not None]
        D=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",str(p)],capture_output=True,text=True).stdout.strip())
        # Trim to the INTENDED span: subsequence-match the scripted line against the transcript,
        # cut at the first & last intended word -> drops leading junk AND trailing improv
        # (so we keep clips that clean() now accepts instead of paying to re-roll them).
        # Canonicalize BOTH sides (reaction strip + got-to/gotta + an/a + number-fold) so the match
        # survives Scribe's digit rendering ("$116 million") and benign word swaps.
        intended,_=_prep(dias[j], intended=True) if j < len(dias) else ([],set())
        cwords,starts,ends=_prep_ts(ws)
        # TIGHTEST-span subsequence match: when the line contains a repeated word (e.g. two
        # "you"s), a greedy first-match latches the EARLIEST occurrence and drags improv that
        # sits between it and the real line into the kept span (omni's "if you give rent, you
        # only pay if you win" left "give rent" in). Try every start index where the first
        # intended word matches, and keep the span that consumes the FEWEST transcript words.
        best=None  # (span_word_count, start_time, end_time)
        for s in range(len(cwords)):
            if not intended or cwords[s]!=intended[0]: continue
            wi=0; en_t=None; consumed=0
            for k in range(s,len(cwords)):
                consumed=k-s+1
                if wi<len(intended) and cwords[k]==intended[wi]:
                    en_t=ends[k]; wi+=1
                    if wi==len(intended): break
            if wi==len(intended) and en_t is not None and starts[s] is not None and (best is None or consumed<best[0]):
                best=(consumed, starts[s], en_t)
        # Scribe CHRONICALLY null-texts the head of the compliance line ("You may qualify...") —
        # it cost Q-18a, W-12, and U-11 their "You may" (turns the locked hedge into a claim).
        # Never word-trim that clip; always keep the full speech span via audio energy.
        force_wide = bool(intended) and " ".join(intended[:3])=="you may qualify"
        if best and not force_wide:
            st, en = best[1], best[2]
        else:
            # Match failed — usually Scribe returning text:null / start:null for edge words
            # ("You may qualify" -> only "qualify" timestamped; cost Q-18a and W-13 their "You may",
            # a COMPLIANCE word). Word-based fallback inherits the same nulls, so use AUDIO ENERGY
            # bounds instead: keep the full speech span via silencedetect (leading/trailing improv
            # risk accepted — rarer than the null-text case).
            sd=subprocess.run(["ffmpeg","-i",str(p),"-af","silencedetect=noise=-35dB:d=0.15","-f","null","-"],
                              capture_output=True,text=True).stderr
            ons=[float(x) for x in re.findall(r"silence_end: ([0-9.]+)",sd)]
            offs=[float(x) for x in re.findall(r"silence_start: ([0-9.]+)",sd)]
            st=ons[0] if ons and (not offs or offs[0]<0.05) else 0.0   # leading silence -> speech onset
            en=offs[-1] if offs and offs[-1]>st+0.2 and (not ons or ons[-1]<offs[-1]) else D  # unclosed trailing silence -> speech end
            if ws:  # never tighter than the timestamped words we DO have
                st=min(st, ws[0]["start"]); en=max(en, ws[-1]["end"])
        st=max(0.0,st-0.03); en=min(D,en+0.05)
        t=DIR/f"_jt{j:02d}.mp4"
        # NOTE: the Veo "Veo" watermark (bottom-right) is removed in ONE ratio-preserving pass at
        # the very end (center-crop 675x1200 -> scale 720x1280, uniform 16/15x, no stretch), not here.
        subprocess.run(["ffmpeg","-y","-ss",f"{st:.3f}","-i",str(p),"-t",f"{en-st:.3f}","-vf","scale=720:1280,fps=24,setsar=1","-c:v","libx264","-preset","fast","-crf","18","-c:a","aac","-ar","44100","-b:a","192k",str(t)],capture_output=True,check=True)
        trimmed.append(t)
    lst=DIR/"_jc.txt"; lst.write_text("".join(f"file '{t.resolve()}'\n" for t in trimmed))
    raw=DIR/"_jcraw.mp4"; subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),"-c","copy",str(raw)],capture_output=True,check=True)
    meas=subprocess.run(["ffmpeg","-i",str(raw),"-af","loudnorm=I=-16:TP=-1.5:print_format=json","-f","null","-"],capture_output=True,text=True)
    mm=re.search(r"\{[^{}]*\"input_i\"[^{}]*\}",meas.stderr.replace("\n"," ")); gn=0.0
    if mm:
        try: gn=-16.0-float(json.loads(mm.group(0))["input_i"])
        except Exception: gn=0.0
    subprocess.run(["ffmpeg","-y","-i",str(raw),"-af",f"volume={gn:.2f}dB,alimiter=limit=0.891","-c:v","copy","-c:a","aac","-b:a","192k",out],capture_output=True,check=True)

if __name__=="__main__":
    letter=sys.argv[1]; persona,tone,text=SCRIPTS[letter]
    globals()['LETTER']=letter
    DIR=ROOT/f"{letter}_{persona}{TAG}_la"; DIR.mkdir(parents=True,exist_ok=True)
    print(f"    model={MODEL}  ref={REF_PARAM}  dir={DIR.name}",flush=True)
    chunks=chunk_for(letter,text)
    print(f"=== {letter} on {persona}: {len(chunks)} chunks ===",flush=True)
    mgid=upload(PERSONAS[persona])
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(do_chunk,[(i,d,mgid,tone) for i,d in enumerate(chunks)]))
    files=[]; dias=[]
    for i in range(len(chunks)):
        if (DIR/f"{i:02d}.mp4").exists():
            files.append(f"{i:02d}.mp4"); dias.append(chunks[i])
        elif (DIR/f"{i:02d}a.mp4").exists() and (DIR/f"{i:02d}b.mp4").exists():
            d1,d2=split_dia(chunks[i]); files+=[f"{i:02d}a.mp4",f"{i:02d}b.mp4"]; dias+=[d1,d2]
        elif (DIR/f"{i:02d}a.mp4").exists():
            d1,_=split_dia(chunks[i]); files.append(f"{i:02d}a.mp4"); dias.append(d1)
        else: print(f"  !! chunk {i:02d} MISSING (gave up)",flush=True)
    print(f"  assembling {len(files)} clips",flush=True)
    out=str(ROOT/f"{letter}{TAG}_full.mp4")
    if files: jumpcut(files,dias,out); print(f"DONE {letter} -> {out}",flush=True)
    else: print(f"DONE {letter} -> NO CLIPS",flush=True)
