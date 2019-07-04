#!/bin/bash
for f in *.stl; do
    meshlabserver -i $f -o $(basename $f .stl).obj
done
