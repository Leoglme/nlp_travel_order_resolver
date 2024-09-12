#!/bin/bash
#Install github cli instruction if not exit on your machine
command -v gh >/dev/null 2>&1 || {
  echo >&2 "please install github cli and run command gh auth login: https://cli.github.com/manual/installation"
  exit 1
}

# Global variable

# Retrieving the current date
date=$(date +"%d/%m/%Y %T")

# Get Your github Name or Username
github_name=$(gh api user -q .name)

if [ -z "$github_name" ]; then
  github_name=$(gh api user -q .login)
fi

get_current_test_branch_id() {
  git fetch
  ids=$(git branch | grep -o ' test-[[:digit:]]\+$' | grep -o '[[:digit:]]\+')
  currentId="0"
  nbLines=$(echo -n "$ids" | grep -c '^')
  for ((c = 0; c < nbLines; c++)); do
    read id
    if ((currentId < id)); then
      currentId=$id
    fi
  done <<<"$ids"
  echo $currentId
}

# Help command

# Fonction for display help
Help() {
  echo "#####################################################################################################"
  echo "#"
  echo "#                                    IZIGIT.SH"
  echo "#"
  echo "# This script allows izidor developers to automate and manage git workflow easily."
  echo "#"
  echo "#####################################################################################################"
  echo ""
  echo
  echo "Syntax: izigit [-s|c|i|p|h]"
  echo "options:"
  echo ""
  echo "create [ticket_number] Create, fetch and checkout branch for ticket ( example: izigit create 654 )"
  echo "reset Reset test branch, so that it is strictly identical to the develop branch ( example: izigit reset )"
  echo "test [ticket_number] Merge issue branch into test branch ( example: izigit test 654 )"
  echo "pr [ticket_number] Creating a pull request from the github issue branch to the develop branch ( example: izigit pr 654 )"
  echo "h     Print this Help."
}

# Creating a pull request from the github issue branch to the develop branch
# Arguments: $2 = ticket number
PrIssueToDevelop() {
  if [ $2 ]; then
    develop_branch=develop
    # Get branch name with ticket number
    issue_branch_name=$(git branch -r | grep $2 | sed 's/  origin\///')

    if [ -z $issue_branch_name ]; then
      echo "No git branch found for ticket $2"
      exit 0
    fi

    # Updates the issue branch, relative to the develop branch
    git checkout $issue_branch_name
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$issue_branch_name" != "$current_branch" ]; then
      echo "Error on 'git checkout $issue_branch_name'"
      exit 0
    fi
    git pull origin $issue_branch_name
    git checkout $develop_branch
    git pull origin $develop_branch
    git merge $develop_branch
    git push origin $issue_branch_name

    # Check if there are any conflicts
    #disable lf and crlf warnings
    git config core.autocrlf false
    if git diff --name-only --diff-filter=U | grep -q "^"; then
      echo "There are merge conflicts to resolve :"
      git diff --name-only --diff-filter=U
      exit 0
    fi

    # Get issue title
    pr_title=$(gh issue view $2 --json title --jq .title)
    # remove special characters from pr_title
    pr_title=${pr_title//[^a-zA-Z0-9 ]/}

    # Create a pull request from the issue branch to the target branch (main)
    # Create a pull request and get its URL
    pr_url=$(gh pr create --base develop --head "$issue_branch_name" -t "$2 $pr_title" -b "" | grep -o 'https://github.com[^ ]*')

    # Get PR number
    pr_number=$(echo "$pr_url" | grep -oP '/pull/\K[0-9]+')

    # Add comment to issue
    comment="$date - create pull request branch $issue_branch_name to $develop_branch - $github_name. [PR #$pr_number]($pr_url)"
    gh issue comment $2 -b "$comment"
    echo $comment
    exit 0
  fi
  echo "Please specify allows ticket number, izigit pr [ticket_number] ( example: izigit pr 654 )"
}

# Fonction for merge issue branch into test branch
# Arguments: $2 = ticket number
MergeIssueInTest() {
  if [ $2 ]; then
    current_test_branch_id="$(get_current_test_branch_id)"
    test_branch="test-$current_test_branch_id"
    # Get branch name with ticket number
    branch_name=$(git branch -r | grep $2 | sed 's/  origin\///')

    if [ -z $branch_name ]; then
      echo "No git branch found for ticket $2"
      exit 0
    fi

    git checkout $test_branch
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$test_branch" != "$current_branch" ]; then
      echo "Error on 'git checkout $test_branch'"
      exit 0
    fi
    git pull origin $test_branch
    git merge $branch_name
    # Detect potential conflicts
    conflicts=$(git diff --name-only --diff-filter=U --relative)
    if [ -z "$conflicts" ]; then
      echo "No conflicts. Merge is done."
    else
      echo "Conflicts on merge. Please resolve it and relaunch the command"
      exit 0
    fi
    git push origin $test_branch

    # Add comment to issue
    comment="$date - merge branch $branch_name into $test_branch - $github_name"
    gh issue comment $2 -b "$comment"
    echo $comment
    exit 0
  fi
  echo "Please specify allows ticket number, izigit test [ticket_number] ( example: izigit test 654 )"
}

# Fonction for reset test branch, so that it is strictly identical to the develop branch
ResetTestToDevelop() {
  current_test_branch_id="$(get_current_test_branch_id)"
  new_test_branch_id=$(($current_test_branch_id + 1))
  test_branch="test-$new_test_branch_id"
  reference_branch="develop"

  # Fetch and checkout the reference branch (develop)
  git fetch
  git checkout $reference_branch
  current_branch=$(git rev-parse --abbrev-ref HEAD)
  if [ "$reference_branch" != "$current_branch" ]; then
    echo "Error on 'git checkout $reference_branch'"
    exit 0
  fi
  git pull $reference_branch

  # Delete all local test-* working branches
  git branch | grep ' test-*' | xargs git branch -D

  # Create a new test branch from the reference branch (develop)
  git checkout -b $test_branch

  # Push the new branch to the remote repository
  git push -u origin $test_branch --force

  comment="$date - $test_branch reset to $reference_branch - $github_name"
  echo $comment
}

# Fonction pour créer une branche pour le ticket et y basculer
# Arguments: $2 = numéro du ticket
CreateBranch() {
  if [ $2 ]; then
    # Récupérer le titre de l'issue via la commande gh
    issue_title=$(gh issue view $2 --json title --jq .title)

    # Enlever les caractères spéciaux du titre de l'issue
    issue_title=${issue_title//[^a-zA-Z0-9 ]/}

    # Remplacer les espaces multiples par un seul espace et trimmer le titre
    issue_title="$(echo -e "${issue_title}" | tr -s ' ' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"

    # Remplacer les espaces par des tirets et ajouter le numéro de l'issue au nom de la branche
    branch_name=$2-${issue_title// /-}
    # Create the issue branch and link the branch to the GitHub issue
    gh issue develop $2 --name $branch_name --base $branch_name

    git fetch origin
    # Checkout to the created branch
    git checkout $branch_name

    # Ajouter un commentaire à l'issue pour lier la branche
    comment="$date - création de la branche $branch_name et lien avec l'issue $2 - $github_name"
    gh issue comment $2 -b "$comment"

    echo $comment
    exit 0
  fi
  echo "Veuillez spécifier le numéro du ticket, izigit create [numéro_ticket] (exemple : izigit create 654)"
}

# Enable options arguments
while getopts "h" option; do
  case $option in
  h)
    Help
    exit
    ;;
  ?)
    printf "Command not found, please use command -h for display help"
    exit 1
    ;;
  esac
done

# Display message if no argument or option supplied
if [ $OPTIND -eq 1 ] && [ $# -eq 0 ]; then echo "An argument is required, please use command -h for display help"; fi

# Enable options
if [ "$1" == "create" ]; then CreateBranch $1 $2; fi
if [ "$1" == "reset" ]; then ResetTestToDevelop; fi
if [ "$1" == "test" ]; then MergeIssueInTest $1 $2; fi
if [ "$1" == "pr" ]; then PrIssueToDevelop $1 $2; fi