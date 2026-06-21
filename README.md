# Applied Cryptography — Project 1

Cryptanalysis of a variant **poly-alphabetic substitution cipher** (a Vigenère-style
cipher over a 27-symbol alphabet — `a–z` plus space — with **random characters inserted**
into the ciphertext). Given only the ciphertext, the program recovers the key length, the
key itself, and the most likely plaintext, with no human in the loop.

Authors: **Avani Tiwari, Jonathan Guan, Jeffrey Rathgeber.**

> The full write-up, including pseudocode and methodology, is in
> [`GuanTiwariRathgeber-report.pdf`](GuanTiwariRathgeber-report.pdf).

---

## The cipher being attacked

- **Alphabet:** 27 symbols — `a`–`z` (0–25) and space (26). No punctuation, no case.
- **Encryption:** classic poly-alphabetic shift. Each character of the plaintext is shifted
  by `key[i % keylen]`, where the key is a sequence of integer shifts.
- **Obfuscation:** random characters are inserted throughout the ciphertext, so the
  ciphertext is *longer* than the plaintext and the slices never line up perfectly. The
  attack is designed to be robust to this noise (which is why it leans on the Index of
  Coincidence and Levenshtein distance rather than exact matching).

---

## How the attack works

The pipeline has three stages, each feeding the next.

### Part I — Recover the key length (Index of Coincidence)

For each candidate key length `t` from 1 to a maximum, the ciphertext is cut into `t`
slices (taking every `t`-th character). The **Index of Coincidence (IOC)** is computed for
each slice and averaged:

```
IOC = 27 · Σ nᵢ(nᵢ − 1) / N(N − 1)
```

where `nᵢ` is the count of each symbol and `N` is the slice length. The IOC spikes at the
true key length and its multiples; a threshold of **1.7** (typical for English) is used to
pick the smallest factor that still scores highly, recovering the true key length.

> Functions: `index_of_coincidence()`, `keylength()`.

### Part II — Recover the key (frequency analysis)

If the key length is correct, each slice is effectively a **mono-alphabetic (Caesar)
shift**. For each slice, the program builds a letter-frequency table and rotates it through
all 27 positions, comparing each rotation against a reference **English letter-frequency
distribution**. The rotation with the least total error is the recovered shift for that
position in the key.

> Functions: `make_frequency_table()`, `best_rotation()`, `find_key()`.

### Part III — Recover the plaintext (decrypt + dictionary match)

The full ciphertext is decrypted with the recovered key, leaving a "noisy" plaintext that
still contains the inserted random characters. Two dictionary-based strategies clean it up,
using **Levenshtein (edit) distance** to tolerate that noise:

- **Test 1 (`dict1.txt`):** the noisy plaintext is compared against 5 candidate plaintexts.
  The one within the edit-distance threshold is returned as the answer.
- **Test 2 (`dict2.txt`):** the noisy plaintext is split into words, and each word is
  matched to the closest dictionary word, reassembling the cleaned plaintext.

> Function: `decipher_message()`.

---

## Repository layout

| File | Purpose |
|------|---------|
| `GuanTiwariRathgeber-decrypt-source.py` | The complete decryption program (all three parts + CLI prompt). |
| `dict1.txt` | **Test 1** dictionary — a header line plus 5 candidate plaintexts, one per "Candidate Plaintext #n" block. |
| `dict2.txt` | **Test 2** dictionary — a header line followed by one word per line. |
| `GuanTiwariRathgeber-report.pdf` | Project report: methodology, pseudocode, and contributions. |

### About the two text files

They are **read automatically** by the script — they are *not* passed as command-line
arguments. The code opens them by hard-coded relative path:

```python
with open('dict1.txt') as f: ...   # line 135
with open('dict2.txt') as f: ...   # line 144
```

So both files must sit in the **current working directory** when you run the program. The
only input supplied at runtime is the ciphertext, entered interactively at a prompt.

> **Note:** `dict1.txt` is parsed assuming an exact layout (a header, blank lines, then five
> `Candidate Plaintext #n` blocks). Swapping in differently-formatted files will cause the
> parser to read the wrong lines silently rather than error out.

---

## Requirements

- **Python 3** (developed/tested on 3.13)
- [`numpy`](https://numpy.org/)
- [`jellyfish`](https://github.com/jamesturk/jellyfish) — provides `levenshtein_distance`

Install the dependencies:

```bash
pip install numpy jellyfish
```

---

## Usage

Run from inside the project directory (so `dict1.txt` and `dict2.txt` are found):

```bash
python GuanTiwariRathgeber-decrypt-source.py
```

You will be prompted:

```
Enter the ciphertext:
```

Paste the ciphertext (lowercase letters and spaces) and press Enter. The program prints its
best plaintext guess:

```
My plaintext guess is: <decrypted text>
```

---

## Limitations & notes

- The IOC key-length step assumes the key does **not** contain an unnatural number of
  repeated letters; pathological keys can throw off the estimate.
- Dictionary parsing is rigid (see note above) — the file formats are tied to the specific
  Test 1 / Test 2 inputs this project was built around.
- Thresholds (IOC ≥ 1.7, Levenshtein error cutoffs) are tuned for English text of the
  expected length and may need adjustment for other corpora.

---

## Reference

1. *Five ways to crack a Vigenère cipher* — National Cipher Challenge 2022.
   <https://www.cipherchallenge.org/wp-content/uploads/2020/12/Five-ways-to-crack-a-Vigenere-cipher.pdf>
