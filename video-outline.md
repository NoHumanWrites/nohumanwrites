# NoHumanWrite — video / podcast outline

Target: 8–10 minutes, one talking head plus screen, published with the paper.

## Title options

1. Everyone is trying to detect AI writing. I built the opposite.
2. Detecting the human in AI-written code
3. Claude now watermarks everything. Good. Here's the tool that reads it.
4. The 23:40 hot-fix problem

## Thumbnail

Split frame. Left: a code diff, all green except three red lines. Right: the words "HUMAN: 3 lines". No face needed.

## Structure

**0:00 Cold open (30 s).** Show the Chase AI video title on screen: "Fable 5.1 watermarks everything, here's how to remove it." Beat. "I watched this and thought: why would I want to remove it? I trust the machine's paragraphs more than my own. The mark tells me which ones are mine."

**0:30 The inversion (90 s).** Every detector asks "did an AI write this?". Wrong question for anyone who writes with agents all day. In my code, the AI's lines came with a prompt, a diff and a test run. My lines came with a coffee. The incidents are in my lines. So: find the human.

**2:00 Why statistics cannot do it (90 s).** On screen: the base-rate arithmetic from the paper. 99 % of human spans caught, 60 % of machine spans falsely flagged, 5 % human prevalence → 8 % precision. "Fewer than one flag in twelve is a person. This is not a tuning problem." One line on Sadasivan's impossibility result, one line on the detectors that flag non-native English speakers.

**3:30 Provenance instead (2 min).** Screen recording: `python3 nhw/attest.py --stats` builds the index from real transcripts in 40 s. Run it on a tool the agent wrote: 96 % attested, the 4 % listed by line number. Run it on a hand-written note: 0 %. "No model, no key, no statistics. The agent logged what it wrote; I read the log."

**5:30 The honest part (90 s).** Run it on the tool's own source: 9 %. "Same agent wrote this. It used a shell command instead of the logged write tool, and the ledger went blind. Any unlogged channel looks like a human. That result is the whole product: provenance has to be signed at the moment of writing, by every tool, or it's a story with holes."

**7:00 What it becomes (60 s).** The GitHub App mock-up: one number on the PR, three red hunks, a policy dropdown. "Sigstore for authorship."

**8:00 The ethics beat (30 s).** "This tool never says a person's work is machine-made. That's the mistake with victims. It only says a machine's work is machine-made, and whatever is left is yours to look at twice."

**8:30 Close (30 s).** Paper link, repo link. "If your team writes with agents, install it on one repo and send me the ratio. I'll publish the distribution."

## B-roll list

- Terminal recordings of the three runs (96 %, 0 %, 9 %) — record at 1.5× then slow to real time for the numbers.
- The bimodal histogram from `eval/corpus-results.json` (draw it in the artifact page; screen-capture).
- Anthropic help-centre page on marking, scrolled slowly.
- The C2PA logo and a Content Credentials "cr" badge as the analogy.

## Podcast variant (25 min)

Same skeleton, plus a guest who ships agent-written code to production. Questions: where did your last incident come from? Did a human type the line? Would you block an unattested hunk? What would you pay per seat to know?
