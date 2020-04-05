Workflow
========

**arackpy** uses Mercurial (hg) for its distributed version control system. In
short there is a default or development branch, a stable branch and one or more
feature branches that can be worked on at any given point.


Default
-------

The default branch is the branch where all work in actively done. A team of
developers will routinely make commits into the default branch. When the
project is at a state it can be released for the next version, the default
branch is merged into the stable branch.


Stable
------

The stable branch is the most current release branch that is maintained by the
project maintainers. It is the branch from which release tags and commits are
made after the default branch is merged into it. Release tag and hotfixes are
merged back from this branch into the default branch.


Feature
-------

Feature branches are offshoots of the development branch used to introduce new
features or fixes without affecting the default development branch after the
default branch is merged into it.
