# Laura Image Studio - Manual Tasks Checklist
# Follow these step-by-step instructions to complete the remaining external tasks.
# Check off each item as you complete it.

**Created:** 2026-03-03
**Estimated Total Time:** 4-6 hours across all tasks

---

## TASK 1: Test All 3 Workflows in ComfyUI (Priority: CRITICAL)

### Why This Matters
The 3 premium workflow JSONs were built programmatically via Python builder scripts. They have been structurally validated (no duplicate IDs, no broken links), but they have NOT been loaded into ComfyUI to verify they actually render and execute correctly. This is the single most important task before any release.

### Pre-Requirements
- ComfyUI running with Laura Image Studio custom nodes loaded
- Check the ComfyUI terminal output on startup -- confirm you see:
  ```
  ## [snrtherock/Laura Studio] All dependencies verified/installed.
  ```
- If you see any `WARNING: Failed to load <module>` messages, fix those FIRST

### Step-by-Step Instructions

#### 1A. Test Community Edition
1. Open ComfyUI in your browser (usually http://127.0.0.1:8188)
2. Click the **Load** button (folder icon) in the top menu bar
3. Navigate to: `workflows/master/Laura_Master_Community_v0.8.json`
4. Click Open
5. **CHECK FOR RED NODES**: Red nodes mean the node class is not installed or the class name doesn't match. Write down EVERY red node name.
6. **CHECK FOR MISSING CONNECTIONS**: Look for any disconnected wires (grey/dangling lines). Each group should have clean connections flowing left-to-right.
7. **CHECK ALL 27 GROUPS**: Scroll right through the entire workflow. Verify all groups are visible:
   - Groups 1-16: Original stages (Model Setup through Final Output -- most should still be in their original positions)
   - Group 17: VRAM & Optimization (x=7400)
   - Group 18: Enhanced Prompts (x=8200)
   - Group 19: Batch Processing (x=9000)
   - Group 20: Tile Processing (x=9800)
   - Group 21: Model Comparison (x=10600)
   - Group 22: Advanced Video (x=11400)
   - Group 23: Cinema Upscale (x=12200)
   - Group 24: Face Animation (x=13000)
   - Group 25: VRAM Cleaner (x=13800)
   - Group 26: Crash Recovery (x=14600)
   - Group 27: Background Library (x=15400)
8. **TEST EXECUTION** (Optional - requires models downloaded):
   - Set a simple text prompt in the Prompt Builder node
   - Load a test image into the Face Reference node
   - Click "Queue Prompt"
   - Watch the terminal for errors
   - If a stage fails, note which stage and the exact error message

#### 1B. Test Studio Edition
1. Repeat all steps from 1A but load: `workflows/master/Laura_Master_Studio_v0.8.json`
2. The Studio edition uses HIGHER-end nodes:
   - Wan22Generator (14B) instead of community's 1.3B
   - CogVideoXGenerator (5B) instead of 2B
   - LauraVideoCinemaUpscale (SUPIR+RIFE) instead of basic UpscaleChain
3. These nodes need more VRAM. If you get OOM errors, that's expected on <12GB -- note it but it's not a bug.

#### 1C. Test Hybrid Edition
1. Repeat all steps from 1A but load: `workflows/master/Laura_Master_Hybrid_v0.8.json`
2. The Hybrid edition has the MOST advanced video pipeline:
   - Multiple video engines (Wan + CogVideoX + Cosmos)
   - LauraVideoFaceDrive (LivePortrait v2 face animation)
   - Full cinema upscale chain
3. This is the heaviest workflow. It's designed for 12GB+ VRAM.

#### What to Do If You Find Problems
- **Red nodes**: The node class name in the JSON doesn't match what's registered in Python. Tell me the exact node title shown in red and I'll fix the class name mapping.
- **Missing connections**: A link in the JSON references a node ID or slot that doesn't exist. Tell me which two nodes should be connected and I'll fix the builder script.
- **Widget value errors**: A node has a widget value that's out of range or invalid type. Tell me the node name and the widget name/value.
- **Import errors on startup**: A Python module failed to load. Copy the full traceback from the terminal.

---

## TASK 2: Set Up Patreon Account (Priority: HIGH)

### Why This Matters
Patreon is where you'll distribute the premium Studio and Hybrid workflow editions. The Community edition stays free on GitHub; the paid workflows are your revenue stream.

### Step-by-Step Instructions

#### 2A. Create Patreon Page
1. Go to https://www.patreon.com/create
2. Sign up / log in with your preferred account
3. Set your **page name**: `snrtherock` or `Laura Image Studio`
4. Set your **category**: "Technology" > "Software"
5. Write your **about section**:
   ```
   Creator of Laura Image Studio - a professional 107-node custom node suite
   for ComfyUI. I build premium AI image and video generation workflows for
   content creators, AI influencers, and digital artists.
   
   Free tier: Community Edition workflow + all 107 custom nodes (open-source)
   Paid tiers: Premium Studio & Hybrid workflows with advanced video generation,
   cinema upscaling, face animation, and multi-engine support.
   ```

#### 2B. Create Tier Structure
**Tier 1 - Supporter ($5/month)**
- Name: "Community Supporter"
- Benefits:
  - Early access to node updates
  - Access to Community Edition workflow (also free on GitHub)
  - Discord supporter role
  - Monthly development update posts

**Tier 2 - Studio ($15/month)**
- Name: "Studio Creator"
- Benefits:
  - Everything in Tier 1
  - Laura_Master_Studio_v0.8.json workflow
  - Studio workflow updates for life of subscription
  - Priority bug fix support
  - Access to studio-only tutorial videos

**Tier 3 - Professional ($30/month)**
- Name: "Professional Creator"
- Benefits:
  - Everything in Tier 2
  - Laura_Master_Hybrid_v0.8.json workflow
  - All future premium workflows
  - 1-on-1 setup support (30 min/month)
  - Custom node requests (voted on monthly)
  - Early beta access to new features

#### 2C. Create Welcome Post
Write a welcome post for new patrons:
```
Welcome to Laura Image Studio!

Here's how to get started:
1. Install ComfyUI (https://github.com/comfyanonymous/ComfyUI)
2. Clone Laura Image Studio into your custom_nodes folder:
   git clone https://github.com/snrtherock/Laura-Image-Studio.git custom_nodes/Laura_Image_Studio
3. Download your tier's workflow from the "Workflow Downloads" post
4. Load the .json file in ComfyUI
5. Follow the WORKFLOW_GUIDE.md included with your download

Need help? Drop a comment or DM me!
```

#### 2D. Create Workflow Distribution Post
1. Create a new post titled "Workflow Downloads - v0.8 Viral Video Edition"
2. Set visibility:
   - Community Edition: Public (everyone)
   - Studio Edition: Tier 2+ only
   - Hybrid Edition: Tier 3 only
3. Attach the JSON files from `workflows/master/`:
   - `Laura_Master_Community_v0.8.json` (public)
   - `Laura_Master_Studio_v0.8.json` (Tier 2+)
   - `Laura_Master_Hybrid_v0.8.json` (Tier 3)
4. Include the `WORKFLOW_GUIDE.md` as an attachment on all tiers

#### 2E. Set Up Your Profile
1. Upload a profile picture (use an AI-generated avatar if you prefer anonymity)
2. Upload a banner image (generate one using your own workflow!)
3. Set your social links (GitHub, YouTube if applicable)
4. Enable the "Free membership" option so people can follow without paying

---

## TASK 3: Set Up Buy Me a Coffee (Priority: MEDIUM)

### Why This Matters
Buy Me a Coffee is a simpler alternative/supplement to Patreon. Some users prefer one-time purchases over subscriptions. This gives you a second revenue channel.

### Step-by-Step Instructions

#### 3A. Create Account
1. Go to https://www.buymeacoffee.com/signup
2. Sign up with your preferred method
3. Set username: `snrtherock`
4. Set page name: "Laura Image Studio"

#### 3B. Create Products (One-Time Purchases)
**Product 1 - Studio Workflow ($25 one-time)**
- Name: "Laura Studio Edition v0.8"
- Description: "Premium ComfyUI workflow with Wan 2.2 14B, CogVideoX 5B, SUPIR cinema upscale. 161 nodes, 27 groups. Requires 12GB+ VRAM."
- File: `Laura_Master_Studio_v0.8.json` + `WORKFLOW_GUIDE.md` (zip them together)
- Price: $25

**Product 2 - Hybrid Workflow ($40 one-time)**
- Name: "Laura Hybrid Edition v0.8"
- Description: "Ultimate ComfyUI workflow with multi-engine video (Wan + CogVideoX + Cosmos), LivePortrait v2 face animation, full cinema pipeline. 160 nodes, 27 groups. Requires 12GB+ VRAM."
- File: `Laura_Master_Hybrid_v0.8.json` + `WORKFLOW_GUIDE.md` (zip them together)
- Price: $40

**Product 3 - Complete Bundle ($55 one-time)**
- Name: "Laura Complete Bundle v0.8"
- Description: "All 3 workflow editions (Community + Studio + Hybrid) plus Node Reference Guide. Best value."
- Files: All 3 JSONs + `WORKFLOW_GUIDE.md` + `NODE_REFERENCE_GUIDE.md` (zip together)
- Price: $55

#### 3C. Set Up Page
1. Write a bio similar to the Patreon about section
2. Enable "Supporters" view so people can see others who bought
3. Add a "thank you" message that auto-sends after purchase with setup instructions

---

## TASK 4: Update GitHub README with Payment Links (Priority: HIGH)

### Why This Matters
Once Patreon and BMAC are set up, you need to add the actual links to your public README so people can find and buy the premium workflows.

### Step-by-Step Instructions

1. Get your Patreon URL: `https://www.patreon.com/snrtherock` (or whatever you chose)
2. Get your BMAC URL: `https://www.buymeacoffee.com/snrtherock`
3. Tell me both URLs and I will update these files for you:
   - `custom_nodes/Laura_Image_Studio/README.md` (replace the placeholder text)
   - `workflows/master/WORKFLOW_GUIDE.md` (replace the placeholder text)
4. Currently both files have: `[Patreon / Buy Me a Coffee] (Links coming soon!)`
5. These will be replaced with actual clickable links

---

## TASK 5: Record Video Tutorials (Priority: LOW - Do After Tasks 1-4)

### Why This Matters
Video tutorials dramatically increase adoption. Most ComfyUI users learn from YouTube. A single good tutorial can drive more traffic than weeks of forum posts.

### Equipment Needed
- Screen recording software: OBS Studio (free) - https://obsproject.com/
- Microphone (optional but recommended): Even a $20 USB mic improves perceived quality
- Video editor (optional): DaVinci Resolve (free) - https://www.blackmagicdesign.com/products/davinciresolve

### Video 1: Quick Start (5-10 minutes)
**Title:** "Laura Image Studio - ComfyUI All-in-One Node Suite (107 Nodes!)"
**Content:**
1. Show the GitHub page, star count, description
2. Demo the installation (git clone into custom_nodes)
3. Show ComfyUI loading with all 107 nodes visible in the node menu
4. Load the Community Edition workflow
5. Walk through the 27 groups visually (scroll right slowly)
6. Run a simple generation end-to-end
7. Show the final output
8. Mention Patreon/BMAC for premium editions

### Video 2: Deep Dive - Virtual Dressing Room (10-15 minutes)
**Title:** "AI Virtual Dressing Room - 10 Clothing Slots with IPAdapter"
**Content:**
1. Explain the dressing room concept
2. Show how the 10 IPAdapter clothing slots work
3. Demo loading different clothing reference images
4. Show face swap integration
5. Show background replacement
6. Run full pipeline and show results
7. Tips for best results (image quality, angles, lighting)

### Video 3: Viral Video Production (10-15 minutes)
**Title:** "Create Viral AI Videos with Wan 2.2 + LivePortrait v2"
**Content:**
1. Show the Studio or Hybrid workflow
2. Explain the video generation stages
3. Demo Wan 2.2 text-to-video generation
4. Show LivePortrait v2 face animation
5. Demo SUPIR + RIFE cinema upscale pipeline
6. Show the final 1080p 60fps output
7. Compare Community vs Studio vs Hybrid results

### Upload Locations
- **YouTube**: Create a channel or use your existing one. Tag with: ComfyUI, AI, image generation, video generation, Wan 2.2, FLUX, custom nodes
- **Patreon**: Post the videos as patron-only content for early access, then make public after 1 week

### Recommended OBS Settings for Tutorials
- Resolution: 1920x1080 (match your ComfyUI window)
- FPS: 30 (sufficient for UI recording)
- Encoder: x264 or NVENC (you have RTX 4070 Ti)
- Bitrate: 6000-8000 kbps for good quality
- Audio: 128kbps AAC

---

## TASK 6: Community Promotion (Priority: LOW - Do After Video Tutorials)

### Where to Post
1. **Reddit**:
   - r/comfyui - Primary audience, post with screenshots
   - r/StableDiffusion - Broader audience
   - r/AIArt - Art-focused community
   - r/LocalLLaMA - Tech-savvy AI enthusiasts
   
2. **GitHub**:
   - Add your repo to the ComfyUI-Manager custom node list (submit PR to: https://github.com/ltdrdata/ComfyUI-Manager)
   - The `node_config.json` we updated is specifically for this
   
3. **CivitAI**:
   - Create a model page linking to your GitHub
   - Upload example outputs generated by your workflows
   
4. **Discord Servers**:
   - ComfyUI Official Discord
   - Stable Diffusion Discord
   - AI Art Discord communities

### How to Submit to ComfyUI-Manager (IMPORTANT)
This is how users discover your nodes through ComfyUI's built-in manager:
1. Fork the repo: https://github.com/ltdrdata/ComfyUI-Manager
2. Edit `custom-node-list.json` and add your entry:
   ```json
   {
     "author": "snrtherock",
     "title": "Laura Image Studio",
     "reference": "https://github.com/snrtherock/Laura-Image-Studio",
     "files": ["https://github.com/snrtherock/Laura-Image-Studio"],
     "install_type": "git-clone",
     "description": "Professional 107-node suite for AI Influencers & Viral Video. Virtual dressing room, face swap/animation, multi-engine video (Wan 2.2, CogVideoX, Cosmos), cinema upscaling, batch/tile processing, VRAM optimization."
   }
   ```
3. Submit a Pull Request to ltdrdata/ComfyUI-Manager
4. Wait for review and merge (usually 1-7 days)

---

## CHECKLIST (Print This and Check Off As You Go)

```
[ ] TASK 1: Test Workflows
    [ ] 1A. Community Edition loads without red nodes
    [ ] 1B. Studio Edition loads without red nodes  
    [ ] 1C. Hybrid Edition loads without red nodes
    [ ] Report any issues found

[ ] TASK 2: Patreon Setup
    [ ] 2A. Created Patreon page
    [ ] 2B. Created 3 tier structure
    [ ] 2C. Published welcome post
    [ ] 2D. Published workflow download post
    [ ] 2E. Completed profile setup

[ ] TASK 3: Buy Me a Coffee Setup
    [ ] 3A. Created BMAC account
    [ ] 3B. Created 3 products
    [ ] 3C. Set up page and auto-messages

[ ] TASK 4: Update Links
    [ ] Got Patreon URL
    [ ] Got BMAC URL
    [ ] Told assistant to update README and WORKFLOW_GUIDE

[ ] TASK 5: Video Tutorials
    [ ] Installed OBS Studio
    [ ] Recorded Video 1: Quick Start
    [ ] Recorded Video 2: Virtual Dressing Room
    [ ] Recorded Video 3: Viral Video Production
    [ ] Uploaded to YouTube

[ ] TASK 6: Community Promotion
    [ ] Posted to r/comfyui
    [ ] Submitted PR to ComfyUI-Manager
    [ ] Created CivitAI page
    [ ] Posted in Discord servers
```

---

*This file is for your personal use. Do NOT commit this to the public GitHub repo.*
*When you complete a task and need code changes, come back and tell me what to update.*
