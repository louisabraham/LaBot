#!/bin/sh

export DofusInvoker="/Applications/Dofus.app/Contents/Data/Dofus.app/Contents/Resources/DofusInvoker.swf"
export selectclass='com.ankamagames.dofus.BuildInfos,com.ankamagames.dofus.network.++,com.ankamagames.jerakine.network.++'
export config='parallelSpeedUp=0'

cd "$( dirname "${BASH_SOURCE[0]}" )"
cd ..

/Applications/FFDec.app/Contents/Resources/ffdec.sh \
  -config "$config" \
    -selectclass "$selectclass" \
      -export script \
        ./sources $DofusInvoker
