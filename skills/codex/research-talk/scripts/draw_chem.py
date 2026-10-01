#!/usr/bin/env python3
"""Quiet 2D structure drawing for slides (RDKit): normal black bonds and coloured heteroatoms, with an optional pale halo behind a substructure.

usage (RDKit python, e.g. the project's chem-env):
  draw_chem.py --smiles "<SMILES>" --out structure.png [--halo-smarts "<SMARTS>"] [--halo-atoms 0,31] [--size 4200x3200]
The halo is drawn first (pale gray-blue), then the plain molecule on top, so the highlighted part is readable but never louder than the molecule.
Do NOT use saturated strokes: a thick cyan scaffold with peach halos was called out as "too prominent" by the user (2026-10-01).
Output is cropped to its ink with a 3 % margin; prints the PNG size and atom pixel positions as JSON for label/leader placement."""
import argparse, json
from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('--smiles', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--halo-smarts'); ap.add_argument('--halo-atoms', default='')
ap.add_argument('--size', default='4200x3200')
ap.add_argument('--bond-length', type=float, default=140); ap.add_argument('--line-width', type=float, default=6)
a = ap.parse_args()
W, H = (int(x) for x in a.size.split('x'))
m = Chem.MolFromSmiles(a.smiles)
rdDepictor.SetPreferCoordGen(True); rdDepictor.Compute2DCoords(m)
ha = [int(x) for x in a.halo_atoms.split(',') if x.strip()]
hb = []
if a.halo_smarts:
    q = Chem.MolFromSmarts(a.halo_smarts)
    match = m.GetSubstructMatch(q)
    hb = [b.GetIdx() for b in m.GetBonds() if b.GetBeginAtomIdx() in match and b.GetEndAtomIdx() in match]
K = a.bond_length / 80
def make():
    d = rdMolDraw2D.MolDraw2DCairo(W, H)
    o = d.drawOptions()
    o.bondLineWidth = a.line_width * K; o.fixedBondLength = a.bond_length; o.padding = 0.06
    o.setBackgroundColour((1, 1, 1, 1)); o.minFontSize = int(34 * K); o.maxFontSize = int(60 * K)
    o.highlightRadius = 0.3; o.fillHighlights = True
    o.highlightBondWidthMultiplier = 2
    return d
HL = dict(highlightAtoms=ha, highlightBonds=hb,
          highlightAtomColors={i: (0.62, 0.74, 0.88) for i in ha}, highlightBondColors={i: (0.82, 0.90, 0.97) for i in hb},
          highlightAtomRadii={i: 0.3 for i in ha})
d = make()
if ha or hb:
    # The halo enlarges the drawing's bounding box, so the plain pass would land a few pixels off. Measure the shift on throw-away drawers,
    # draw the halo first, then draw the plain molecule on top with the compensating offset.
    d_h = make(); d_h.DrawMolecule(m, **HL); p_h = d_h.GetDrawCoords(0)
    d_p = make(); d_p.DrawMolecule(m); p_p = d_p.GetDrawCoords(0)
    d.DrawMolecule(m, **HL)
    d.SetOffset(int(round(p_h.x - p_p.x)), int(round(p_h.y - p_p.y)))
d.DrawMolecule(m)
d.FinishDrawing()
open(a.out, 'wb').write(d.GetDrawingText())
im = Image.open(a.out).convert('RGB'); arr = np.asarray(im)
ys, xs = np.where(arr.min(axis=2) < 250)
pad = int(max(xs.max() - xs.min(), ys.max() - ys.min()) * 0.03)
box = (max(0, xs.min() - pad), max(0, ys.min() - pad), min(im.width, xs.max() + pad + 1), min(im.height, ys.max() + pad + 1))
im.crop(box).save(a.out)
atoms = {i: [float(d.GetDrawCoords(i).x - box[0]), float(d.GetDrawCoords(i).y - box[1])] for i in range(m.GetNumAtoms())}
print(json.dumps({'png': a.out, 'width': int(box[2] - box[0]), 'height': int(box[3] - box[1]), 'atoms': atoms}))
