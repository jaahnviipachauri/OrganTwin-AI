"""
Digital organ-on-chip physics (simplified, demo-grade).

Each organ holds a physiological state vector that drifts with drug exposure.
Values are clamped to biologically plausible ranges used in OoC literature.
"""

from __future__ import annotations

import random
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone

DRUGS = {
    "Paracetamol": {
        "display": "Paracetamol (Acetaminophen)",
        "toxicity": 0.2,
        "class": "moderate",
        "note": "Common analgesic. Hepatotoxic at high doses.",
    },
    "Ibuprofen": {
        "display": "Ibuprofen",
        "toxicity": 0.25,
        "class": "moderate",
        "note": "NSAID. Nephrotoxic at high doses.",
    },
    "Aspirin": {
        "display": "Aspirin",
        "toxicity": 0.15,
        "class": "moderate",
        "note": "NSAID and antiplatelet. Can cause GI bleeding.",
    },
    "Naproxen": {
        "display": "Naproxen",
        "toxicity": 0.2,
        "class": "moderate",
        "note": "NSAID. Moderate nephrotoxicity risk.",
    },
    "Diclofenac": {
        "display": "Diclofenac",
        "toxicity": 0.3,
        "class": "moderate",
        "note": "NSAID. Associated with hepatotoxicity and nephrotoxicity.",
    },
    "Celecoxib": {
        "display": "Celecoxib",
        "toxicity": 0.15,
        "class": "moderate",
        "note": "COX-2 inhibitor. Lower GI risk, but cardiovascular concerns.",
    },
    "Indomethacin": {
        "display": "Indomethacin",
        "toxicity": 0.35,
        "class": "severe",
        "note": "Potent NSAID. High risk of renal impairment.",
    },
    "Ketorolac": {
        "display": "Ketorolac",
        "toxicity": 0.4,
        "class": "severe",
        "note": "Strong NSAID. High risk for GI bleed and renal failure limit use to 5 days.",
    },
    "Meloxicam": {
        "display": "Meloxicam",
        "toxicity": 0.2,
        "class": "moderate",
        "note": "NSAID with preferential COX-2 inhibition.",
    },
    "Etoricoxib": {
        "display": "Etoricoxib",
        "toxicity": 0.15,
        "class": "moderate",
        "note": "COX-2 inhibitor.",
    },
    "Amoxicillin": {
        "display": "Amoxicillin",
        "toxicity": 0.05,
        "class": "safe",
        "note": "Penicillin antibiotic. Generally well tolerated.",
    },
    "Ampicillin": {
        "display": "Ampicillin",
        "toxicity": 0.05,
        "class": "safe",
        "note": "Penicillin antibiotic.",
    },
    "Penicillin": {
        "display": "Penicillin",
        "toxicity": 0.05,
        "class": "safe",
        "note": "Beta-lactam antibiotic.",
    },
    "Azithromycin": {
        "display": "Azithromycin",
        "toxicity": 0.1,
        "class": "safe",
        "note": "Macrolide antibiotic. Rare hepatic risk.",
    },
    "Clarithromycin": {
        "display": "Clarithromycin",
        "toxicity": 0.15,
        "class": "moderate",
        "note": "Macrolide. Can cause QT prolongation and liver stress.",
    },
    "Erythromycin": {
        "display": "Erythromycin",
        "toxicity": 0.2,
        "class": "moderate",
        "note": "Macrolide. Higher incidence of GI and hepatic issues.",
    },
    "Doxycycline": {
        "display": "Doxycycline",
        "toxicity": 0.1,
        "class": "safe",
        "note": "Tetracycline antibiotic.",
    },
    "Minocycline": {
        "display": "Minocycline",
        "toxicity": 0.15,
        "class": "moderate",
        "note": "Tetracycline. Rare autoimmune hepatotoxicity.",
    },
    "Ciprofloxacin": {
        "display": "Ciprofloxacin",
        "toxicity": 0.25,
        "class": "moderate",
        "note": "Fluoroquinolone. Tendonitis risk and moderate renal excretion.",
    },
    "Levofloxacin": {
        "display": "Levofloxacin",
        "toxicity": 0.2,
        "class": "moderate",
        "note": "Fluoroquinolone antibiotic.",
    },
    "Metformin": {
        "display": "Metformin",
        "toxicity": 0.1,
        "class": "safe",
        "note": "Biguanide for T2DM. Lactic acidosis risk if renal impairment exists.",
    },
    "Glimepiride": {
        "display": "Glimepiride",
        "toxicity": 0.15,
        "class": "moderate",
        "note": "Sulfonylurea. Risk of hypoglycemia.",
    },
    "Amlodipine": {
        "display": "Amlodipine",
        "toxicity": 0.05,
        "class": "safe",
        "note": "Calcium channel blocker. Safe profile.",
    },
    "Losartan": {
        "display": "Losartan",
        "toxicity": 0.08,
        "class": "safe",
        "note": "ARB for hypertension. Renal protective in diabetes.",
    },
    "Telmisartan": {
        "display": "Telmisartan",
        "toxicity": 0.08,
        "class": "safe",
        "note": "ARB for hypertension.",
    },
    "Atorvastatin": {
        "display": "Atorvastatin",
        "toxicity": 0.25,
        "class": "moderate",
        "note": "Statin. Potential for transaminitis (liver stress) and myopathy.",
    },
    "Rosuvastatin": {
        "display": "Rosuvastatin",
        "toxicity": 0.2,
        "class": "moderate",
        "note": "Statin. Strong lipid-lowering with some renal clearance.",
    },
    "Clopidogrel": {
        "display": "Clopidogrel",
        "toxicity": 0.15,
        "class": "moderate",
        "note": "Antiplatelet agent. Requires hepatic activation.",
    },
    "Warfarin": {
        "display": "Warfarin",
        "toxicity": 0.35,
        "class": "severe",
        "note": "Anticoagulant. Narrow therapeutic index; bleeding risk.",
    },
    "Apixaban": {
        "display": "Apixaban",
        "toxicity": 0.1,
        "class": "safe",
        "note": "DOAC anticoagulant. Predictable profile.",
    },
    "Salbutamol": {
        "display": "Salbutamol (Albuterol)",
        "toxicity": 0.05,
        "class": "safe",
        "note": "Beta-2 agonist. Safe pulmonary profile.",
    },
    "Budesonide": {
        "display": "Budesonide",
        "toxicity": 0.1,
        "class": "safe",
        "note": "Corticosteroid. High first-pass metabolism limits systemic toxicity.",
    },
    "Montelukast": {
        "display": "Montelukast",
        "toxicity": 0.05,
        "class": "safe",
        "note": "Leukotriene receptor antagonist.",
    },
    "Prednisolone": {
        "display": "Prednisolone",
        "toxicity": 0.3,
        "class": "moderate",
        "note": "Systemic corticosteroid. Metabolic and immune side effects.",
    },
    "Omeprazole": {
        "display": "Omeprazole",
        "toxicity": 0.05,
        "class": "safe",
        "note": "PPI. Very well tolerated.",
    },
    "Pantoprazole": {
        "display": "Pantoprazole",
        "toxicity": 0.05,
        "class": "safe",
        "note": "PPI. Safe hepatic profile.",
    },
    "Ondansetron": {
        "display": "Ondansetron",
        "toxicity": 0.05,
        "class": "safe",
        "note": "Anti-emetic. Safe, minor QT prolongation risk.",
    },
    "Sertraline": {
        "display": "Sertraline",
        "toxicity": 0.1,
        "class": "safe",
        "note": "SSRI antidepressant. Hepatic metabolism.",
    },
    "Fluoxetine": {
        "display": "Fluoxetine",
        "toxicity": 0.1,
        "class": "safe",
        "note": "SSRI antidepressant.",
    },
    "Escitalopram": {
        "display": "Escitalopram",
        "toxicity": 0.1,
        "class": "safe",
        "note": "SSRI antidepressant.",
    },
    "Alprazolam": {
        "display": "Alprazolam",
        "toxicity": 0.15,
        "class": "moderate",
        "note": "Benzodiazepine. Liver metabolized, potential for CNS depression.",
    },
    "Clonazepam": {
        "display": "Clonazepam",
        "toxicity": 0.15,
        "class": "moderate",
        "note": "Benzodiazepine.",
    },
    "Diazepam": {
        "display": "Diazepam",
        "toxicity": 0.2,
        "class": "moderate",
        "note": "Benzodiazepine. Long half-life with active hepatic metabolites.",
    },
    "Olanzapine": {
        "display": "Olanzapine",
        "toxicity": 0.25,
        "class": "moderate",
        "note": "Atypical antipsychotic. Metabolic syndrome and hepatic stress.",
    },
    "Risperidone": {
        "display": "Risperidone",
        "toxicity": 0.2,
        "class": "moderate",
        "note": "Atypical antipsychotic. Renal excretion and hepatic metabolism.",
    },
    "Levetiracetam": {
        "display": "Levetiracetam",
        "toxicity": 0.05,
        "class": "safe",
        "note": "Anticonvulsant. Low hepatic metabolism, mostly renally excreted.",
    },
    "Gabapentin": {
        "display": "Gabapentin",
        "toxicity": 0.05,
        "class": "safe",
        "note": "Anticonvulsant. Not metabolized by liver, pure renal excretion.",
    },
    "Cetirizine": {
        "display": "Cetirizine",
        "toxicity": 0.02,
        "class": "safe",
        "note": "Second-gen antihistamine. Very safe.",
    },
    "Loratadine": {
        "display": "Loratadine",
        "toxicity": 0.02,
        "class": "safe",
        "note": "Second-gen antihistamine. Extensive hepatic metabolism but safe.",
    },
    "Hydroxychloroquine": {
        "display": "Hydroxychloroquine",
        "toxicity": 0.4,
        "class": "severe",
        "note": "Antimalarial/DMARD. Risk of retinal and cardiotoxicity.",
    },
    "Lisinopril": {
        "display": "Lisinopril",
        "toxicity": 0.17,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Ramipril": {
        "display": "Ramipril",
        "toxicity": 0.03,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Enalapril": {
        "display": "Enalapril",
        "toxicity": 0.08,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Valsartan": {
        "display": "Valsartan",
        "toxicity": 0.07,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Irbesartan": {
        "display": "Irbesartan",
        "toxicity": 0.19,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Candesartan": {
        "display": "Candesartan",
        "toxicity": 0.18,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Bisoprolol": {
        "display": "Bisoprolol",
        "toxicity": 0.23,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Metoprolol": {
        "display": "Metoprolol",
        "toxicity": 0.04,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Carvedilol": {
        "display": "Carvedilol",
        "toxicity": 0.12,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Atenolol": {
        "display": "Atenolol",
        "toxicity": 0.03,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Propranolol": {
        "display": "Propranolol",
        "toxicity": 0.07,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Nebivolol": {
        "display": "Nebivolol",
        "toxicity": 0.14,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Diltiazem": {
        "display": "Diltiazem",
        "toxicity": 0.03,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Verapamil": {
        "display": "Verapamil",
        "toxicity": 0.07,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Nifedipine": {
        "display": "Nifedipine",
        "toxicity": 0.17,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Furosemide": {
        "display": "Furosemide",
        "toxicity": 0.15,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Hydrochlorothiazide": {
        "display": "Hydrochlorothiazide",
        "toxicity": 0.07,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Spironolactone": {
        "display": "Spironolactone",
        "toxicity": 0.16,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Eplerenone": {
        "display": "Eplerenone",
        "toxicity": 0.21,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Torsemide": {
        "display": "Torsemide",
        "toxicity": 0.02,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Digoxin": {
        "display": "Digoxin",
        "toxicity": 0.21,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Amiodarone": {
        "display": "Amiodarone",
        "toxicity": 0.54,
        "class": "moderate",
        "note": "Amiodarone has a narrow therapeutic index. Organ stress expected at high doses.",
    },
    "Sotalol": {
        "display": "Sotalol",
        "toxicity": 0.1,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Flecainide": {
        "display": "Flecainide",
        "toxicity": 0.06,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Propafenone": {
        "display": "Propafenone",
        "toxicity": 0.24,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Nitroglycerin": {
        "display": "Nitroglycerin",
        "toxicity": 0.1,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Isosorbide": {
        "display": "Isosorbide",
        "toxicity": 0.04,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Ranolazine": {
        "display": "Ranolazine",
        "toxicity": 0.04,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Simvastatin": {
        "display": "Simvastatin",
        "toxicity": 0.21,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Pravastatin": {
        "display": "Pravastatin",
        "toxicity": 0.16,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Lovastatin": {
        "display": "Lovastatin",
        "toxicity": 0.21,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Fluvastatin": {
        "display": "Fluvastatin",
        "toxicity": 0.19,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Pitavastatin": {
        "display": "Pitavastatin",
        "toxicity": 0.14,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Ezetimibe": {
        "display": "Ezetimibe",
        "toxicity": 0.24,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Fenofibrate": {
        "display": "Fenofibrate",
        "toxicity": 0.11,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Gemfibrozil": {
        "display": "Gemfibrozil",
        "toxicity": 0.15,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Alirocumab": {
        "display": "Alirocumab",
        "toxicity": 0.21,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Evolocumab": {
        "display": "Evolocumab",
        "toxicity": 0.16,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Sitagliptin": {
        "display": "Sitagliptin",
        "toxicity": 0.22,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Vildagliptin": {
        "display": "Vildagliptin",
        "toxicity": 0.15,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Saxagliptin": {
        "display": "Saxagliptin",
        "toxicity": 0.18,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Linagliptin": {
        "display": "Linagliptin",
        "toxicity": 0.03,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Empagliflozin": {
        "display": "Empagliflozin",
        "toxicity": 0.07,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Dapagliflozin": {
        "display": "Dapagliflozin",
        "toxicity": 0.09,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Canagliflozin": {
        "display": "Canagliflozin",
        "toxicity": 0.04,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Semaglutide": {
        "display": "Semaglutide",
        "toxicity": 0.07,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Liraglutide": {
        "display": "Liraglutide",
        "toxicity": 0.04,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Dulaglutide": {
        "display": "Dulaglutide",
        "toxicity": 0.08,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Exenatide": {
        "display": "Exenatide",
        "toxicity": 0.17,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Gliclazide": {
        "display": "Gliclazide",
        "toxicity": 0.1,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Glyburide": {
        "display": "Glyburide",
        "toxicity": 0.11,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Pioglitazone": {
        "display": "Pioglitazone",
        "toxicity": 0.07,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Insulin Glargine": {
        "display": "Insulin Glargine",
        "toxicity": 0.08,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Citalopram": {
        "display": "Citalopram",
        "toxicity": 0.24,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Paroxetine": {
        "display": "Paroxetine",
        "toxicity": 0.17,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Venlafaxine": {
        "display": "Venlafaxine",
        "toxicity": 0.16,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Duloxetine": {
        "display": "Duloxetine",
        "toxicity": 0.06,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Desvenlafaxine": {
        "display": "Desvenlafaxine",
        "toxicity": 0.19,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Mirtazapine": {
        "display": "Mirtazapine",
        "toxicity": 0.06,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Bupropion": {
        "display": "Bupropion",
        "toxicity": 0.11,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Trazodone": {
        "display": "Trazodone",
        "toxicity": 0.25,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Amitriptyline": {
        "display": "Amitriptyline",
        "toxicity": 0.17,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Nortriptyline": {
        "display": "Nortriptyline",
        "toxicity": 0.15,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Lithium": {
        "display": "Lithium",
        "toxicity": 0.54,
        "class": "moderate",
        "note": "Lithium has a narrow therapeutic index. Organ stress expected at high doses.",
    },
    "Valproate": {
        "display": "Valproate",
        "toxicity": 0.21,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Lamotrigine": {
        "display": "Lamotrigine",
        "toxicity": 0.2,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Carbamazepine": {
        "display": "Carbamazepine",
        "toxicity": 0.07,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Topiramate": {
        "display": "Topiramate",
        "toxicity": 0.03,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Pregabalin": {
        "display": "Pregabalin",
        "toxicity": 0.09,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Quetiapine": {
        "display": "Quetiapine",
        "toxicity": 0.08,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Aripiprazole": {
        "display": "Aripiprazole",
        "toxicity": 0.07,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Haloperidol": {
        "display": "Haloperidol",
        "toxicity": 0.24,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Clozapine": {
        "display": "Clozapine",
        "toxicity": 0.22,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Lurasidone": {
        "display": "Lurasidone",
        "toxicity": 0.09,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Ziprasidone": {
        "display": "Ziprasidone",
        "toxicity": 0.17,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Donepezil": {
        "display": "Donepezil",
        "toxicity": 0.11,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Memantine": {
        "display": "Memantine",
        "toxicity": 0.23,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Rivastigmine": {
        "display": "Rivastigmine",
        "toxicity": 0.13,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Ropinirole": {
        "display": "Ropinirole",
        "toxicity": 0.08,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Pramipexole": {
        "display": "Pramipexole",
        "toxicity": 0.08,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Levodopa": {
        "display": "Levodopa",
        "toxicity": 0.15,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Selegiline": {
        "display": "Selegiline",
        "toxicity": 0.08,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Rasagiline": {
        "display": "Rasagiline",
        "toxicity": 0.15,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Lansoprazole": {
        "display": "Lansoprazole",
        "toxicity": 0.23,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Rabeprazole": {
        "display": "Rabeprazole",
        "toxicity": 0.11,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Esomeprazole": {
        "display": "Esomeprazole",
        "toxicity": 0.07,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Famotidine": {
        "display": "Famotidine",
        "toxicity": 0.25,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Ranitidine": {
        "display": "Ranitidine",
        "toxicity": 0.14,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Metoclopramide": {
        "display": "Metoclopramide",
        "toxicity": 0.04,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Domperidone": {
        "display": "Domperidone",
        "toxicity": 0.03,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Loperamide": {
        "display": "Loperamide",
        "toxicity": 0.05,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Mesalazine": {
        "display": "Mesalazine",
        "toxicity": 0.16,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Sulfasalazine": {
        "display": "Sulfasalazine",
        "toxicity": 0.2,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Formoterol": {
        "display": "Formoterol",
        "toxicity": 0.12,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Salmeterol": {
        "display": "Salmeterol",
        "toxicity": 0.03,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Tiotropium": {
        "display": "Tiotropium",
        "toxicity": 0.11,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Ipratropium": {
        "display": "Ipratropium",
        "toxicity": 0.25,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Fluticasone": {
        "display": "Fluticasone",
        "toxicity": 0.14,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Beclometasone": {
        "display": "Beclometasone",
        "toxicity": 0.24,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Theophylline": {
        "display": "Theophylline",
        "toxicity": 0.22,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Omalizumab": {
        "display": "Omalizumab",
        "toxicity": 0.02,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Mepolizumab": {
        "display": "Mepolizumab",
        "toxicity": 0.19,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Codeine": {
        "display": "Codeine",
        "toxicity": 0.18,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Tramadol": {
        "display": "Tramadol",
        "toxicity": 0.14,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Morphine": {
        "display": "Morphine",
        "toxicity": 0.24,
        "class": "moderate",
        "note": "Opioid analgesic. Primarily CNS depressant, but hepatically metabolized.",
    },
    "Oxycodone": {
        "display": "Oxycodone",
        "toxicity": 0.3,
        "class": "moderate",
        "note": "Opioid analgesic. Primarily CNS depressant, but hepatically metabolized.",
    },
    "Fentanyl": {
        "display": "Fentanyl",
        "toxicity": 0.22,
        "class": "moderate",
        "note": "Opioid analgesic. Primarily CNS depressant, but hepatically metabolized.",
    },
    "Buprenorphine": {
        "display": "Buprenorphine",
        "toxicity": 0.12,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Methotrexate": {
        "display": "Methotrexate",
        "toxicity": 0.12,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Adalimumab": {
        "display": "Adalimumab",
        "toxicity": 0.24,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Etanercept": {
        "display": "Etanercept",
        "toxicity": 0.22,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Infliximab": {
        "display": "Infliximab",
        "toxicity": 0.08,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Rituximab": {
        "display": "Rituximab",
        "toxicity": 0.14,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Allopurinol": {
        "display": "Allopurinol",
        "toxicity": 0.06,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Febuxostat": {
        "display": "Febuxostat",
        "toxicity": 0.23,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Colchicine": {
        "display": "Colchicine",
        "toxicity": 0.22,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Cefuroxime": {
        "display": "Cefuroxime",
        "toxicity": 0.09,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Ceftriaxone": {
        "display": "Ceftriaxone",
        "toxicity": 0.17,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Meropenem": {
        "display": "Meropenem",
        "toxicity": 0.16,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Gentamicin": {
        "display": "Gentamicin",
        "toxicity": 0.55,
        "class": "severe",
        "note": "Gentamicin is notoriously nephrotoxic. Requires therapeutic drug monitoring.",
    },
    "Amikacin": {
        "display": "Amikacin",
        "toxicity": 0.73,
        "class": "severe",
        "note": "Amikacin is notoriously nephrotoxic. Requires therapeutic drug monitoring.",
    },
    "Vancomycin": {
        "display": "Vancomycin",
        "toxicity": 0.66,
        "class": "severe",
        "note": "Vancomycin is notoriously nephrotoxic. Requires therapeutic drug monitoring.",
    },
    "Linezolid": {
        "display": "Linezolid",
        "toxicity": 0.2,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Teicoplanin": {
        "display": "Teicoplanin",
        "toxicity": 0.14,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Fluconazole": {
        "display": "Fluconazole",
        "toxicity": 0.02,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Itraconazole": {
        "display": "Itraconazole",
        "toxicity": 0.09,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Voriconazole": {
        "display": "Voriconazole",
        "toxicity": 0.02,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Amphotericin": {
        "display": "Amphotericin",
        "toxicity": 0.78,
        "class": "severe",
        "note": "Amphotericin is notoriously nephrotoxic. Requires therapeutic drug monitoring.",
    },
    "Acyclovir": {
        "display": "Acyclovir",
        "toxicity": 0.22,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Valacyclovir": {
        "display": "Valacyclovir",
        "toxicity": 0.21,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Oseltamivir": {
        "display": "Oseltamivir",
        "toxicity": 0.09,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Tenofovir": {
        "display": "Tenofovir",
        "toxicity": 0.03,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Entecavir": {
        "display": "Entecavir",
        "toxicity": 0.22,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Sofosbuvir": {
        "display": "Sofosbuvir",
        "toxicity": 0.24,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Remdesivir": {
        "display": "Remdesivir",
        "toxicity": 0.04,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Nirmatrelvir": {
        "display": "Nirmatrelvir",
        "toxicity": 0.13,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Cyclophosphamide": {
        "display": "Cyclophosphamide",
        "toxicity": 0.72,
        "class": "severe",
        "note": "Cyclophosphamide is a potent chemotherapy agent with significant systemic toxicity.",
    },
    "Fluorouracil": {
        "display": "Fluorouracil",
        "toxicity": 0.89,
        "class": "severe",
        "note": "Fluorouracil is a potent chemotherapy agent with significant systemic toxicity.",
    },
    "Paclitaxel": {
        "display": "Paclitaxel",
        "toxicity": 0.89,
        "class": "severe",
        "note": "Paclitaxel is a potent chemotherapy agent with significant systemic toxicity.",
    },
    "Docetaxel": {
        "display": "Docetaxel",
        "toxicity": 0.73,
        "class": "severe",
        "note": "Docetaxel is a potent chemotherapy agent with significant systemic toxicity.",
    },
    "Imatinib": {
        "display": "Imatinib",
        "toxicity": 0.82,
        "class": "severe",
        "note": "Imatinib is a potent chemotherapy agent with significant systemic toxicity.",
    },
    "Trastuzumab": {
        "display": "Trastuzumab",
        "toxicity": 0.15,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Pembrolizumab": {
        "display": "Pembrolizumab",
        "toxicity": 0.08,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Nivolumab": {
        "display": "Nivolumab",
        "toxicity": 0.22,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Cyclosporine": {
        "display": "Cyclosporine",
        "toxicity": 0.48,
        "class": "moderate",
        "note": "Cyclosporine has a narrow therapeutic index. Organ stress expected at high doses.",
    },
    "Tacrolimus": {
        "display": "Tacrolimus",
        "toxicity": 0.44,
        "class": "moderate",
        "note": "Tacrolimus has a narrow therapeutic index. Organ stress expected at high doses.",
    },
    "Mycophenolate": {
        "display": "Mycophenolate",
        "toxicity": 0.14,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Azathioprine": {
        "display": "Azathioprine",
        "toxicity": 0.19,
        "class": "moderate",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
    "Sirolimus": {
        "display": "Sirolimus",
        "toxicity": 0.07,
        "class": "safe",
        "note": "Standard pharmaceutical compound. Normal metabolic processing via liver/kidneys.",
    },
}

ORGAN_UNITS = {
    "lungs": {
        "oxygen": "%",
        "ph": "",
        "compliance": "%",
        "surfactant": "%",
        "stress_level": "%",
        "damage_percent": "%",
        "viability": "%",
        "lactate": "mmol/L",
        "toxic_metabolites": "mg/dL",
        "heartbeat": "bpm",
        "contractility": "%",
        "filtration": "mL/min",
        "glucose": "mg/dL",
    },

    "liver": {
        "oxygen": "%",
        "glucose": "mg/dL",
        "lactate": "mmol/L",
        "ph": "pH",
        "viability": "%",
    },
    "heart": {
        "heartbeat": "bpm",
        "contractility": "%",
        "oxygen": "%",
        "ph": "pH",
    },
    "kidney": {
        "filtration": "mL/min",
        "oxygen": "%",
        "viability": "%",
        "toxic_metabolites": "AU",
    },
}

BASELINES = {
    "lungs": {
        "oxygen": 99.0,
        "ph": 7.4,
        "compliance": 100.0,
        "surfactant": 100.0,
        "stress_level": 0.0,
        "damage_percent": 0.0,
        "viability": 100.0,
        "lactate": 1.0,
        "toxic_metabolites": 0.0,
        "heartbeat": 0.0,
        "contractility": 0.0,
        "filtration": 0.0,
        "glucose": 0.0,
    },

    "liver": {
        "oxygen": 97.4,
        "glucose": 96.0,
        "lactate": 0.85,
        "ph": 7.40,
        "viability": 98.2,
    },
    "heart": {
        "heartbeat": 72.0,
        "contractility": 92.0,
        "oxygen": 96.8,
        "ph": 7.40,
    },
    "kidney": {
        "filtration": 110.0,
        "oxygen": 95.5,
        "viability": 97.6,
        "toxic_metabolites": 1.1,
    },
}


@dataclass
class OrganChip:
    organ: str
    state: dict[str, float] = field(default_factory=dict)
    previous: dict[str, float] = field(default_factory=dict)
    active_drugs: list[str] = field(default_factory=list)
    drug: str = "None"
    dose_mg: float = 0.0
    duration_h: float = 0.0
    exposure_elapsed_h: float = 0.0
    age_group: str = "18-64"
    history: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.state = deepcopy(BASELINES[self.organ])
        self.previous = deepcopy(self.state)

    def apply_drug(self, drugs: list[str], dose_mg: float, duration_h: float, age_group: str = "18-64") -> None:
        for d in drugs:
            if d not in DRUGS:
                raise ValueError(f"Unknown drug: {d}")
        self.active_drugs = drugs
        self.drug = " + ".join(drugs) if drugs else "None"
        self.dose_mg = dose_mg
        self.duration_h = duration_h
        self.age_group = age_group
        self.exposure_elapsed_h = 0.0

    def clear_drug(self) -> None:
        self.active_drugs = []
        self.drug = "None"
        self.dose_mg = 0.0
        self.duration_h = 0.0
        self.exposure_elapsed_h = 0.0
        self.age_group = "18-64"

    def tick(self, dt_hours: float) -> None:
        self.previous = deepcopy(self.state)
        noise = lambda sigma: random.gauss(0, sigma)
        
        # Calculate combined toxicity
        tox = sum(DRUGS.get(d, {}).get("toxicity", 0.0) for d in getattr(self, "active_drugs", []))
        
        # Age-based vulnerability multiplier
        age_multiplier = 1.0
        if getattr(self, "age_group", "18-64") in ["0-1", "65+"]:
            age_multiplier = 1.6
        elif getattr(self, "age_group", "18-64") in ["1-3", "3-12"]:
            age_multiplier = 1.3
        elif getattr(self, "age_group", "18-64") == "12-18":
            age_multiplier = 1.1

        
        remaining = max(self.duration_h - self.exposure_elapsed_h, 0.0) if self.drug != "None" else 0.0
        active = 1.0 if remaining > 0 else 0.0
        potency = tox * (self.dose_mg / 30.0) * active * age_multiplier
        
        # Calculate drug-drug synergy combinations specifically for glucose spikes
        num_drugs = len(getattr(self, "active_drugs", []))
        combo_spike = 0.0
        if num_drugs > 1 and active:
            # Glucose spikes quadratically with the number of combined drugs due to metabolic overload
            combo_spike = (num_drugs ** 2) * 5.0 * tox * (self.dose_mg / 30.0)

        # Time-on-chip increases cumulative insult
        self.exposure_elapsed_h += dt_hours * active
        accum = min(self.exposure_elapsed_h / max(self.duration_h, 0.1), 1.5) if active else 0.0
        insult = potency * (0.35 + 0.65 * accum)

        s = self.state
        if self.organ == "liver":
            s["oxygen"] += noise(0.35) - 9.5 * insult * dt_hours
            s["glucose"] += noise(0.8) - 7.0 * insult * dt_hours + combo_spike * dt_hours * 15.0
            s["lactate"] += abs(noise(0.04)) + 1.8 * insult * dt_hours
            s["ph"] += noise(0.004) - 0.12 * insult * dt_hours
            s["viability"] += noise(0.2) - 11.0 * insult * dt_hours
        elif self.organ == "heart":
            s["oxygen"] += noise(0.3) - 8.8 * insult * dt_hours
            s["ph"] += noise(0.004) - 0.11 * insult * dt_hours
            s["contractility"] += noise(0.35) - 12.5 * insult * dt_hours
            # Arrhythmia: tachycardia then pump failure
            if insult < 0.55:
                s["heartbeat"] += noise(0.6) + 14 * insult * dt_hours
            else:
                s["heartbeat"] += noise(1.2) - 18 * insult * dt_hours
        else:
            s["oxygen"] += noise(0.32) - 9.0 * insult * dt_hours
            s["viability"] += noise(0.22) - 12.0 * insult * dt_hours
            s["filtration"] += noise(0.7) - 16.0 * insult * dt_hours
            s["toxic_metabolites"] += abs(noise(0.08)) + 6.5 * insult * dt_hours

        if active == 0:
            for k, base_val in BASELINES[self.organ].items():
                if k in s:
                    s[k] += (base_val - s[k]) * 0.02

        self._clamp()
        self._record()

    def _clamp(self) -> None:
        limits = {
            "oxygen": (22, 100),
            "glucose": (25, 800),
            "lactate": (0.2, 12),
            "ph": (6.65, 7.65),
            "viability": (5, 100),
            "heartbeat": (22, 180),
            "contractility": (8, 100),
            "filtration": (8, 140),
            "toxic_metabolites": (0.1, 60),
        }
        for key, (lo, hi) in limits.items():
            if key in self.state:
                self.state[key] = float(min(hi, max(lo, self.state[key])))

    def _record(self) -> None:
        snapshot = {
            "t": datetime.now(timezone.utc).isoformat(),
            **{k: round(v, 3) for k, v in self.state.items()},
        }
        self.history.append(snapshot)
        if len(self.history) > 360:
            self.history = self.history[-360:]

    def health_score(self) -> float:
        s = self.state
        if self.organ == "liver":
            score = (
                0.28 * (s["oxygen"] / 100)
                + 0.32 * (s["viability"] / 100)
                + 0.22 * max(0, 1 - abs(s["ph"] - 7.4) / 0.4)
                + 0.18 * max(0, 1 - s["lactate"] / 8)
            )
        elif self.organ == "heart":
            hr_pen = abs(s["heartbeat"] - 72) / 80
            score = (
                0.3 * (s["oxygen"] / 100)
                + 0.35 * (s["contractility"] / 100)
                + 0.2 * max(0, 1 - hr_pen)
                + 0.15 * max(0, 1 - abs(s["ph"] - 7.4) / 0.4)
            )
        else:
            score = (
                0.28 * (s["oxygen"] / 100)
                + 0.32 * (s["viability"] / 100)
                + 0.25 * (s["filtration"] / 120)
                + 0.15 * max(0, 1 - s["toxic_metabolites"] / 30)
            )
        return round(100 * min(1.0, max(0.0, score)), 1)

    def twin_metrics(self) -> dict:
        health = self.health_score()
        damage = round(100 - health, 1)
        stress = round(min(100, damage * 1.15 + (self.dose_mg * DRUGS.get(self.drug, {}).get("toxicity", 0) * 0.4)), 1)
        survival = round(max(4, min(99.5, 100 - damage * 1.05 - abs(7.4 - self.state.get("ph", 7.4)) * 40)), 1)
        if health >= 88:
            condition = "Homeostatic"
        elif health >= 72:
            condition = "Compensated stress"
        elif health >= 52:
            condition = "Decompensating"
        else:
            condition = "Critical failure risk"
        eta = None
        if health < 78 and self.drug in ("Drug B", "Drug C"):
            if "viability" in self.state:
                slope = max(self.previous.get("viability", 98) - self.state.get("viability", 98), 0.05)
            else:
                slope = max(self.previous.get("contractility", 92) - self.state.get("contractility", 92), 0.05)
            eta = round(max(2.0, (health - 40) / (slope * 8)), 1)
        return {
            "health_score": health,
            "stress_level": stress,
            "survival_rate": survival,
            "damage_percent": damage,
            "condition": condition,
            "failure_eta_min": eta,
        }

    def feature_vector(self) -> dict:
        merged = {
            "dose_mg": self.dose_mg,
            "duration_h": max(self.duration_h, self.exposure_elapsed_h),
            "oxygen": self.state.get("oxygen", 96),
            "ph": self.state.get("ph", 7.4),
            "viability": self.state.get("viability", 96),
            "lactate": self.state.get("lactate", 0.9),
            "toxic_metabolites": self.state.get("toxic_metabolites", 1.2),
            "heartbeat": self.state.get("heartbeat", 72),
            "contractility": self.state.get("contractility", 90),
            "filtration": self.state.get("filtration", 105),
            "glucose": self.state.get("glucose", 95),
            "organ": self.organ,
        }
        return merged
