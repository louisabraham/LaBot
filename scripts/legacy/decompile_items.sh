#!/bin/bash

if ! command -v python3 &>/dev/null; then
    echo "Cannot proceed without a python 3 installation!"
    exit 1
fi


export i18n="/Applications/Dofus.app/Contents/Data/Dofus.app/Contents/Resources/data/i18n/"
export common="/Applications/Dofus.app/Contents/Data/Dofus.app/Contents/Resources/data/common/"
export elements="/Applications/Dofus.app/Contents/Data/Dofus.app/Contents/Resources/content/maps/elements.ele"
export maps="/Applications/Dofus.app/Contents/Data/Dofus.app/Contents/Resources/content/maps/"


if [ ! -d "./sources/data" ]; then
    mkdir -p "./sources/data";
else
    rm "./sources/data/"*
fi
if [ ! -d "./input" ]; then
    mkdir -p "./input";
fi
if [ ! -d "./output" ]; then
    mkdir -p "./output";
fi

# First do the i18n file

echo "Decompiling internationalisation files..."

for file in  "$i18n"*".d2i"; do
    python3 "./PyDofus/d2i_unpack.py" "$file"
done

cp "$i18n"*".json" "./sources/data/"

# Then all the d2o files

echo "Decompiling object files..."

cp "$common"*.d2o "./input"
python3 "./PyDofus/d2o_unpack.py"
mv "./output/"* "./sources/data/"
rm "./input/"*
# Finally the map files:

echo "Decompiling map files..."

echo "Map files are huge and take a long time to decompile (~40minutes). Do you want to decompile them now? (y/n)"

read -r answer

while [[ $answer != "y" && $answer != "n" ]] ; do
  echo "Please answer (y)es or (n)o"
  read -r answer
done;

if [[ $answer == "n" ]]; then
  rm -rf "./input"
  rm -rf "./output"
  exit 0;
fi;

python3 "./PyDofus/ele_unpack.py" "$elements"
cp "${elements/.ele/.json}" "./sources/data/"

cp "$maps"*".d2p" "./input/"
python3 "./PyDofus/d2p_unpack.py"

for file in "./output/"*"/"*"/"*".dlm"; do
  python3 "./PyDofus/dlm_unpack.py" "$file"
done; 
rm "./output/"*"/"*"/"*".dlm"
cp "./output/*" "./sources/data"

rm -rf "./input"
rm -rf "./output"
