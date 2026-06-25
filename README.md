# Pioneet Streamlit Demo

This repository contains a Streamlit demo app for presenting the Pioneet customer experience with lightweight, demo-ready data. It is intended for quick local review, GitHub sharing, and deployment to Streamlit Community Cloud.

## Repository Files

- `requirements.txt`: Python packages needed by the Streamlit app.
- `.streamlit/config.toml`: Streamlit UI theme and server defaults.
- `.gitignore`: Local Python, Streamlit secret, editor, and build artifacts to keep out of Git.
- `README.md`: Setup, run, upload, deployment, demo, and QC notes.

## Local Setup

Use Python 3.10 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If your machine uses `py` instead of `python`, replace `python` with `py` in the commands above.

## Run Locally

Start the app from the repository root:

```powershell
streamlit run app.py
```

If the app entry file uses a different name, replace `app.py` with the correct Streamlit file.

## Upload to GitHub

From the repository root:

```powershell
git status
git add README.md requirements.txt .gitignore .streamlit/config.toml
git commit -m "Add Streamlit deployment files"
git branch -M main
git remote add origin https://github.com/YOUR-ORG/YOUR-REPO.git
git push -u origin main
```

If the remote already exists, update it with:

```powershell
git remote set-url origin https://github.com/YOUR-ORG/YOUR-REPO.git
git push -u origin main
```

## Deploy to Streamlit Community Cloud

1. Push the repository to GitHub.
2. Go to [Streamlit Community Cloud](https://streamlit.io/cloud).
3. Select **New app**.
4. Choose the GitHub repository and branch.
5. Set the main file path, usually `app.py`.
6. Confirm that `requirements.txt` is detected.
7. Deploy the app.

If the app needs private keys or credentials later, add them in Streamlit Cloud under **App settings > Secrets**. Do not commit `.streamlit/secrets.toml`.

## Demo Customer Instructions

Use the deployed Streamlit URL during customer walkthroughs.

Recommended demo flow:

1. Open the app in a fresh browser window.
2. Confirm the page loads without install prompts or errors.
3. Walk through the primary scenario from top to bottom.
4. Use any filters, controls, or tabs in a realistic order.
5. Call out that the data is sample data for demonstration only.
6. End by showing the expected customer outcome or decision point.

Before sharing externally, confirm the URL, demo script, and any customer-specific talking points with the project owner.

## Demo Data Note

This demo should use synthetic, anonymized, or approved sample data only. Do not upload real customer data, private credentials, internal exports, or personally identifiable information unless the project owner has explicitly approved that data for the demo environment.

## QC Checks Before Final

Run these checks before handing off the repository or deployment:

- `git status` shows only the intended files changed.
- `pip install -r requirements.txt` completes in a clean virtual environment.
- `streamlit run app.py` starts successfully from the repository root.
- The app loads locally without uncaught Streamlit errors.
- All visible controls, filters, links, and charts work with demo data.
- The deployed Streamlit Cloud app builds successfully from GitHub.
- The deployed app opens in an incognito/private browser window.
- No secrets, tokens, local paths, customer data, or private files are committed.
- `.streamlit/secrets.toml`, `.env`, virtual environments, caches, and editor files are ignored.
- README setup and deployment commands match the final repository structure.
