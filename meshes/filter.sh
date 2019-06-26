#!/bin/bash
for f in *.stl; do
    meshlabserver -i $f -o $f
done
