#!/usr/bin/env python3
"""20 future Depo b-roll stills (gpt-image-2 t2i). Documentary-real. Text-free EXCEPT the
credibility/record shots, which carry REAL, verified text (BMJ 2024 study; MDL No. 3140; Depo =
medroxyprogesterone acetate). Skip-if-exists. Run: [--only a,b]
"""
import sys, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import kie_client as kie

OUT = Path("outputs/depo_interview/broll_future"); OUT.mkdir(parents=True, exist_ok=True)
DOC = ("Photoreal news/documentary cinematography (Frontline / PBS Newshour look), natural "
       "real-world lighting, slight grain, NOT cinematic, NOT stylized.")
NOTEXT = " ABSOLUTELY no on-screen text, no captions, no logos, no readable words."
TEXTRULE = (" Render the specified on-image text EXACTLY as written, spelled correctly, clearly "
            "legible, with NO extra words and NO garbled text.")

# (name, prompt, allow_text)
ITEMS = [
 # A — neuro / surgery journey
 ("A1_neuro_model", "A neurosurgeon in a consult room pointing at a detailed 3D anatomical model of the human brain, indicating one spot with a pen, explaining to a patient seated across the desk. " + DOC, False),
 ("A2_surgical_marking", "Close-up of a patient's partially shaved scalp being marked with a purple surgical skin-marker by a gloved hand, prepping for brain surgery. " + DOC, False),
 ("A3_mri_compare", "A radiology monitor showing two brain MRI scans side by side — the left with a rounded mass near the surface, the right clear after removal. Over-the-shoulder documentary framing. " + DOC, False),
 ("A4_neuro_rehab", "A woman in her forties doing balance and walking rehabilitation, a physical therapist steadying her arm in a bright rehab gym, a short healing scar on her scalp. " + DOC, False),
 ("A5_postop_meds", "An open weekly pill organizer on a kitchen counter beside a few amber prescription bottles and a glass of water, soft morning light. Documentary close-up. " + DOC, False),
 # B — Depo-specific proof
 ("B1_shot_record", "A printed patient injection-record card on a clinic desk with a column of dates spaced a few months apart and the drug name 'Depo-Provera' written in the rows, a pen beside it. Documentary close-up. Text on the card reads 'Depo-Provera' and injection dates. " + DOC, True),
 ("B2_pharmacy_handoff", "A pharmacist handing a 'Depo-Provera' medication box across a pharmacy counter to a customer's hand. The box reads 'Depo-Provera'. Documentary framing. " + DOC, True),
 ("B3_chart_depo", "A medical-records page on a clipboard listing injection history, several rows reading 'Depo-Provera injection' with dates. Documentary close-up. " + DOC, True),
 ("B4_clinic_checkin", "A woman in her forties checking in at a clinic front desk, handing a small appointment card to a receptionist. " + DOC, False),
 # C — process (paper form to replace the empty phone screen)
 ("C1_paper_form", "Close-up of a woman's hands filling out a paper intake form with a pen, printed field labels reading 'Name', 'Date', and 'Diagnosis' with handwriting in the blanks. Documentary close-up. " + DOC, True),
 # D — credibility, REAL verified text
 ("D1_bmj_study", "A laptop screen showing a medical research journal article, the headline title reading 'Use of progestogens and the risk of intracranial meningioma' with 'BMJ 2024' beneath it; a person reading over the shoulder. " + DOC, True),
 ("D2_bmj_stat", "A close-up of a printed medical study page on a desk with one line highlighted in yellow reading 'Medroxyprogesterone acetate: 5.6x risk of intracranial meningioma'. " + DOC, True),
 ("D3_mdl_filing", "A close-up of a formal legal court document on a desk, the header reading 'In re: Depo-Provera Products Liability Litigation' and below it 'MDL No. 3140', a pen resting on the page. " + DOC, True),
 ("D4_fda_warning", "A close-up of an official drug safety label document reading 'Depo-Provera (medroxyprogesterone acetate)' with a bold line 'WARNING: Meningioma' underneath. " + DOC, True),
 ("D6_package_insert", "A Depo-Provera prescribing-information leaflet unfolded on a table, the warnings paragraph with the word 'meningioma' clearly visible, reading glasses beside it. " + DOC, True),
 # E — emotional
 ("E1_scar_mirror", "A Black woman in her forties looking at the healing surgical scar on the side of her shaved scalp in a bathroom mirror, gently touching it, quiet and reflective. " + DOC, False),
 ("E2_hair_cover", "A Black woman in her forties at a mirror parting and styling her hair to cover a scalp surgery scar, soft morning light. " + DOC, False),
 ("E3_legal_notice", "A woman in her forties sitting at a kitchen table reading a formal legal letter with a serious, worried expression, morning light. " + DOC, False),
 ("E4_hug_family", "A woman in her forties hugging her teenage child at home, both with gentle emotional expressions, warm light. " + DOC, False),
 ("E5_waiting_alone", "A woman in her forties sitting alone in a hospital waiting room looking worried, empty chairs around her. " + DOC, False),
]

def gen(name, prompt, allow_text):
    out = OUT / f"{name}.png"
    if out.exists(): print("skip", name); return
    full = prompt + (TEXTRULE if allow_text else NOTEXT)
    res = kie.generate_gpt_image(full, aspect_ratio="9:16", resolution="2K")
    if res.get("status") == "success" and res.get("urls"):
        kie.download(res["urls"][0], out); print("done", name)
    else: print("FAIL", name, str(res.get("raw"))[:160])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only", default="")
    a = ap.parse_args()
    items = ITEMS if not a.only else [x for x in ITEMS if x[0] in set(a.only.split(","))]
    for it in items: gen(*it)
    print("ALL DONE")

if __name__ == "__main__":
    main()
