import subprocess
import json

def extract_metadata(content: str):
    # write the content to a file
    filepath = "tmp/readme.txt"
    with open(filepath, "w") as f:
        f.write(content)

    # run SOMEF to extract metadata
    outname = f"tmp/{filepath}_metadata.json"
    subprocess.run(["somef", "describe", "-d", filepath, "-o", outname])  

    # open the metadata file and read it
    with open(outname, "r") as f:
        metadata = json.load(f)
    
    # remove the metadata file
    subprocess.run(["rm", outname])

    # return the metadata
    return metadata

if __name__ == "__main__":
    readme = "SH_Worker is a simple worker for the SH system. It is written in Python and is licensed under a MIT license. It is designed to be run in a Docker container."
    metadata = extract_metadata(readme)
    print(metadata)