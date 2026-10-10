# Commands Reference

## One-Time Setup
```bash
/opt/anaconda3/bin/playwright install chromium
```

## Export Everything (PNGs + GIFs + MP4s)
```bash
cd /Users/aaryantiwari/Desktop/My_Folder/Lln
./run.sh
```

## Export PNGs Only
```bash
./run.sh export
```

## Create GIFs + MP4s Only
```bash
./run.sh gif
```

## Create GIF + MP4 for a Single Post
```bash
./run.sh gif Post0
./run.sh gif Post1
./run.sh gif Post5
```

## Create New Posts
1. Drop document in `Docs/` folder
2. Open Claude Code
3. Say: **"Create LinkedIn posts from Docs/filename.md"**
4. Approve the plan
5. Run:
./run.sh




To create new posts:

Drop document in Docs/
Open Claude Code → say: "Create LinkedIn posts from Docs/filename.md"
I do everything (HTML + captions + update scripts)
You run: ./run.sh