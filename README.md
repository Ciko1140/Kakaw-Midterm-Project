# Kakaw-Midterm-Project
> Penjadwalan Kelas Mata Kuliah Menggunakan Pendekatan Local Search Optimization.

<p align="center">
<a href="/doc">Project Report</a>
</p>

---

## Team
Kelompok 5: Kakaw

<div align="center" id="contributor">

### Contributors

<table align="center">
  <tr align="left">
    <td><b>NRP</b></td>
    <td><b>Name</b></td>
    <td align="center"><b>GitHub</b></td>
  </tr>
  <tr align="left">
    <td>5025251204</td>
    <td>Althof Rahmatullah</td>
    <td align="center">
      <a href="https://github.com/Linney1">
        <img src="https://github.com/Linney1.png" width="48" alt="Linney1"/><br/>
        <sub><b> @Linney1 </b></sub>
      </a>
    </td>
  </tr>
  <tr align="left">
    <td>5025251183</td>
    <td>Aditya Hariyadi Tjujitno</td>
    <td align="center">
      <a href="https://github.com/adityahariyadit-hash">
        <img src="https://github.com/adityahariyadit-hash.png" width="48" alt="adityahariyadit-hash"/><br/>
        <sub><b> @adityahariyadit-hash </b></sub>
      </a>
    </td>
  </tr>
  <tr align="left">
    <td>5025251084</td>
    <td>Radhit Akriandra</td>
    <td align="center">
      <a href="https://github.com/dhitshine">
        <img src="https://github.com/dhitshine.png" width="48" alt="dhitshine"/><br/>
        <sub><b> @dhitshine </b></sub>
      </a>
    </td>
  </tr>
  <tr align="left">
    <td>5025251206</td>
    <td>Rexa Matutu Harsaputra</td>
    <td align="center">
      <a href="https://github.com/rexaeca">
        <img src="https://github.com/rexaeca.png" width="48" alt="rexaeca"/><br/>
        <sub><b> @rexaeca </b></sub>
      </a>
    </td>
  </tr>
  <tr align="left">
    <td>5025251211</td>
    <td>Rizqi Ardiansyah Putra P.</td>
    <td align="center">
      <a href="https://github.com/Ciko1140">
        <img src="https://github.com/Ciko1140.png" width="48" alt="Ciko1140"/><br/>
        <sub><b> @Ciko1140 </b></sub>
      </a>
    </td>
  </tr>
</table>

</div>

## Description
Kakaw adalah sistem penjadwalan kelas mata kuliah paralel dengan menggunakan pendekatan local search.

## Project Structure
```
.
├── doc
│   └── .gitkeep
├── src
│   └── kakaw
│       ├── __init__.py       # CLI & main
│       ├── algorithms        # HC, SA, GA
│       ├── models            # Room, Student, CourseClass
│       ├── problems          # State, ObjectiveFunction, Problem
│       └── utils             # Parser
├── tests
│   └── sample.json           # instance Kecil
├── pyproject.toml            # Metadata project
├── .python-version           # Versi Python
├── .gitignore                # Abaikan tracking file atau direktori
├── uv.lock
├── PROBLEM-DETAIL.md                # Spesifikasi formal problem
├── PROBLEM-DESCRIPTION.md          # Penjelasan problem
└── README.md 

```

## Requirements
- Python Versions 3.14 or newer
- uv Versions 0.12 or newer (recommended package manager)

## Installation
- Clone repositorinya
```sh
git clone https://github.com/dhitshine/Kakaw-Midterm-Project.git && cd Kakaw-Midterm-Project
```
- Buat virtual environtment dengan `uv`
```sh
uv venv
```
- Install dependencies
```sh
uv sync
```
## Usage
### Steepest Ascent Hill-Climbing
```sh
uv run kakaw --test tests/sample.json --algorithm steepest-hc --plot output.png
```
### Simulated Annealing
```sh
uv run kakaw --test tests/sample.json --algorithm simulated --plot output.png --seed 42
```
`output.png` berisi kurva `F` terhadap `evaluations` untuk run tersebut.

### Genetic Algorithm
```sh
uv run kakaw --test tests/sample.json --algorithm genetic --plot output.png
```
### Help
```sh
uv run kakaw --help
```
