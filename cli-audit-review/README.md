# cli-audit-review

`cli-audit-review` is a scored review skill for strict infrastructure and automation reviews.

**Author:** [ThomasD343](https://github.com/ThomasD343)

It reviews changes through the chain:

```text
contract -> validation -> execution -> proof -> documentation -> release safety
```

## Best Fit

- Ansible roles and collections
- Molecule scenarios
- GitLab CI/CD
- semantic-release and package metadata
- Go/Cobra CLIs
- PowerShell called from Ansible
- shell and Python helper scripts
- Kubernetes/container/runtime changes
- Terraform/OpenTofu infrastructure code
- operator documentation

## Output

The skill produces:

- a decision: `REQUEST_CHANGES`, `COMMENT`, `APPROVE_WITH_NOTES`, or `APPROVE`;
- an RMI score out of 10;
- gate status;
- weighted scorecard;
- findings ordered by production risk;
- smallest next actions;
- positive practices found.

## Installation

Copy the whole `cli-audit-review/` directory into your skills directory.

## Usage

```text
/cli-audit-review path/to/diff.patch
/cli-audit-review roles/my_role
/cli-audit-review .
```

## Privacy

The skill contains only generalized and anonymized review methodology. It must not reveal private source material, personal names, private URLs, organization names, commit hashes, or copied private review comments.
