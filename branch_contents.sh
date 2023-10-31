#!/bin/bash

# Fetch all remote branches (if you want to include remote branches)
git fetch

# List all branches
for branch in $(git branch -a | grep -v HEAD | sed 's/* //'); do
    echo "===== Branch: $branch ====="
    
    # Get the list of all files and directories in the branch
    for item in $(git ls-tree -r --name-only $branch); do
        echo $item
    done

    echo ""  # Just for an empty line for better separation
done
