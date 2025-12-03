#!/usr/bin/env python3
"""
ArgoCD ApplicationSet Migration Utility

Migrates ApplicationSets from SCM generators to Git generators with JSON data structures.
"""

import typer
import yaml
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from azure.devops.connection import Connection
from azure.devops.v7_0.git.models import (
    GitRefUpdate,
    GitCommitRef,
    GitChange,
    ItemContentType,
    VersionControlChangeType,
    GitPullRequest,
)
from msrest.authentication import BasicAuthentication

app = typer.Typer(help="ArgoCD ApplicationSet migration utility")
console = Console()


def load_applicationset(file_path: Path) -> Dict[str, Any]:
    """Load and parse an ApplicationSet YAML file"""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def extract_template_fields(appset_yaml: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key fields from ApplicationSet template"""
    try:
        template = appset_yaml['spec']['template']
        
        return {
            'name': template['metadata']['name'],
            'project': template['spec']['project'],
            'path': template['spec']['source']['path'],
            'repoUrl': template['spec']['source']['repoURL'],
            'targetRevision': template['spec']['source']['targetRevision']
        }
    except KeyError as e:
        raise ValueError(f"Missing required field in template: {e}")


def is_scm_generator(appset_yaml: Dict[str, Any]) -> bool:
    """Check if ApplicationSet uses SCM generator"""
    generators = appset_yaml.get('spec', {}).get('generators', [])
    for gen in generators:
        if 'scmProvider' in gen or 'scm' in gen:
            return True
    return False


def transform_to_git_generator(
    appset_yaml: Dict[str, Any],
    json_file_path: str,
    config_repo_url: str
) -> Dict[str, Any]:
    """Transform SCM generator ApplicationSet to Git generator"""
    
    new_appset = {
        'apiVersion': appset_yaml['apiVersion'],
        'kind': 'ApplicationSet',
        'metadata': appset_yaml['metadata'],
        'spec': {
            'generators': [{
                'git': {
                    'repoURL': config_repo_url,
                    'revision': 'HEAD',
                    'files': [{
                        'path': json_file_path
                    }]
                }
            }],
            'template': appset_yaml['spec']['template']
        }
    }
    
    # Update template to use JSON field references
    template = new_appset['spec']['template']
    template['metadata']['name'] = '{{name}}'
    template['spec']['project'] = '{{project}}'
    template['spec']['source']['path'] = '{{path}}'
    template['spec']['source']['repoURL'] = '{{repoUrl}}'
    template['spec']['source']['targetRevision'] = '{{targetRevision}}'
    
    return new_appset


class AzureDevOpsClient:
    """Azure DevOps Git client for creating branches and pull requests"""
    
    def __init__(self, organization_url: str, pat: str, project: str, repo: str):
        credentials = BasicAuthentication('', pat)
        self.connection = Connection(base_url=organization_url, creds=credentials)
        self.git_client = self.connection.clients.get_git_client()
        self.project = project
        self.repo = repo
        
        # Get repository details
        self.repository = self.git_client.get_repository(project=project, repository_id=repo)
    
    def get_default_branch(self) -> str:
        """Get the default branch of the repository"""
        return self.repository.default_branch.replace('refs/heads/', '')
    
    def get_branch_ref(self, branch_name: str) -> str:
        """Get the full ref for a branch"""
        if not branch_name.startswith('refs/heads/'):
            return f'refs/heads/{branch_name}'
        return branch_name
    
    def branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists"""
        try:
            ref = self.get_branch_ref(branch_name)
            refs = self.git_client.get_refs(
                repository_id=self.repository.id,
                project=self.project,
                filter=ref
            )
            return len(refs) > 0
        except:
            return False
    
    def create_branch(self, branch_name: str, source_branch: Optional[str] = None) -> str:
        """Create a new branch from source branch (defaults to default branch)"""
        if source_branch is None:
            source_branch = self.get_default_branch()
        
        source_ref = self.get_branch_ref(source_branch)
        target_ref = self.get_branch_ref(branch_name)
        
        # Get the commit from source branch
        refs = self.git_client.get_refs(
            repository_id=self.repository.id,
            project=self.project,
            filter=source_ref
        )
        
        if not refs:
            raise ValueError(f"Source branch {source_branch} not found")
        
        source_commit = refs[0].object_id
        
        # Create the new branch
        ref_update = GitRefUpdate(
            name=target_ref,
            old_object_id='0000000000000000000000000000000000000000',
            new_object_id=source_commit
        )
        
        self.git_client.update_refs(
            ref_updates=[ref_update],
            repository_id=self.repository.id,
            project=self.project
        )
        
        console.print(f"[green]✓ Created branch: {branch_name}[/green]")
        return source_commit
    
    def commit_files(
        self,
        branch_name: str,
        files: Dict[str, str],
        commit_message: str
    ) -> str:
        """
        Commit files to a branch.
        files: dict of {path: content}
        """
        branch_ref = self.get_branch_ref(branch_name)
        
        # Get current commit
        refs = self.git_client.get_refs(
            repository_id=self.repository.id,
            project=self.project,
            filter=branch_ref
        )
        
        if not refs:
            raise ValueError(f"Branch {branch_name} not found")
        
        old_commit_id = refs[0].object_id
        
        # Create changes
        changes = []
        for file_path, content in files.items():
            change = GitChange(
                change_type=VersionControlChangeType.add,
                item={'path': f'/{file_path}'},
                new_content={
                    'content': content,
                    'content_type': ItemContentType.raw_text
                }
            )
            changes.append(change)
        
        # Create commit
        commit = GitCommitRef(
            comment=commit_message,
            changes=changes
        )
        
        # Push commit
        push = self.git_client.create_push(
            push={
                'refUpdates': [GitRefUpdate(
                    name=branch_ref,
                    old_object_id=old_commit_id
                )],
                'commits': [commit]
            },
            repository_id=self.repository.id,
            project=self.project
        )
        
        new_commit_id = push.commits[0].commit_id
        console.print(f"[green]✓ Committed {len(files)} file(s) to {branch_name}[/green]")
        console.print(f"  Commit ID: {new_commit_id}")
        
        return new_commit_id
    
    def create_pull_request(
        self,
        source_branch: str,
        target_branch: str,
        title: str,
        description: str,
        reviewers: Optional[List[str]] = None
    ) -> int:
        """Create a pull request"""
        source_ref = self.get_branch_ref(source_branch)
        target_ref = self.get_branch_ref(target_branch)
        
        pr = GitPullRequest(
            source_ref_name=source_ref,
            target_ref_name=target_ref,
            title=title,
            description=description
        )
        
        created_pr = self.git_client.create_pull_request(
            git_pull_request_to_create=pr,
            repository_id=self.repository.id,
            project=self.project
        )
        
        console.print(f"[green]✓ Created Pull Request #{created_pr.pull_request_id}[/green]")
        console.print(f"  URL: {created_pr.url}")
        
        return created_pr.pull_request_id


@app.command()
def migrate(
    input_dir: Path = typer.Argument(
        ...,
        help="Directory containing ApplicationSet YAML files",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True
    ),
    output_dir: Path = typer.Option(
        None,
        "--output-dir", "-o",
        help="Output directory for transformed ApplicationSets (defaults to input_dir/migrated)"
    ),
    json_output: Path = typer.Option(
        "applications.json",
        "--json-output", "-j",
        help="Output path for JSON data file"
    ),
    config_repo_url: str = typer.Option(
        ...,
        "--config-repo", "-r",
        help="Git repository URL where JSON data file will be stored"
    ),
    json_path_in_repo: str = typer.Option(
        "applicationsets/data.json",
        "--json-path",
        help="Path to JSON file within the config repo"
    ),
    appsets_path_in_repo: str = typer.Option(
        "applicationsets/manifests",
        "--appsets-path",
        help="Path where transformed ApplicationSets will be stored in repo"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview changes without writing files"
    ),
    filter_scm_only: bool = typer.Option(
        True,
        "--scm-only/--all",
        help="Only process ApplicationSets with SCM generators"
    ),
    # Azure DevOps options
    create_pr: bool = typer.Option(
        False,
        "--create-pr",
        help="Create a pull request in Azure DevOps"
    ),
    ado_org: Optional[str] = typer.Option(
        None,
        "--ado-org",
        help="Azure DevOps organization URL (e.g., https://dev.azure.com/myorg)",
        envvar="ADO_ORG"
    ),
    ado_project: Optional[str] = typer.Option(
        None,
        "--ado-project",
        help="Azure DevOps project name",
        envvar="ADO_PROJECT"
    ),
    ado_repo: Optional[str] = typer.Option(
        None,
        "--ado-repo",
        help="Azure DevOps repository name",
        envvar="ADO_REPO"
    ),
    ado_pat: Optional[str] = typer.Option(
        None,
        "--ado-pat",
        help="Azure DevOps Personal Access Token",
        envvar="ADO_PAT"
    ),
    branch_name: str = typer.Option(
        "feature/migrate-applicationsets-to-git-generator",
        "--branch",
        help="Branch name for the migration"
    ),
    target_branch: str = typer.Option(
        "main",
        "--target-branch",
        help="Target branch for the pull request"
    ),
    pr_title: Optional[str] = typer.Option(
        None,
        "--pr-title",
        help="Pull request title"
    ),
    pr_description: Optional[str] = typer.Option(
        None,
        "--pr-description",
        help="Pull request description"
    )
):
    """
    Migrate ApplicationSets from SCM generators to Git generators with JSON data structure.
    """
    
    # Validate ADO parameters if creating PR
    if create_pr:
        if not all([ado_org, ado_project, ado_repo, ado_pat]):
            console.print("[red]Error: --create-pr requires --ado-org, --ado-project, --ado-repo, and --ado-pat[/red]")
            console.print("These can also be set via environment variables: ADO_ORG, ADO_PROJECT, ADO_REPO, ADO_PAT")
            raise typer.Exit(1)
    
    # Set default output directory
    if output_dir is None:
        output_dir = input_dir / "migrated"
    
    # Find all YAML files
    yaml_files = list(input_dir.glob("*.yaml")) + list(input_dir.glob("*.yml"))
    
    if not yaml_files:
        console.print(f"[yellow]No YAML files found in {input_dir}[/yellow]")
        raise typer.Exit(1)
    
    console.print(f"[blue]Found {len(yaml_files)} YAML files[/blue]")
    
    # Process files
    applications_data = []
    processed_files = []
    skipped_files = []
    errors = []
    
    for yaml_file in yaml_files:
        try:
            console.print(f"\n[cyan]Processing: {yaml_file.name}[/cyan]")
            
            appset = load_applicationset(yaml_file)
            
            # Check if it's an ApplicationSet
            if appset.get('kind') != 'ApplicationSet':
                console.print(f"  [yellow]⊘ Skipping: Not an ApplicationSet[/yellow]")
                skipped_files.append((yaml_file.name, "Not an ApplicationSet"))
                continue
            
            # Check if it uses SCM generator
            if filter_scm_only and not is_scm_generator(appset):
                console.print(f"  [yellow]⊘ Skipping: Not using SCM generator[/yellow]")
                skipped_files.append((yaml_file.name, "Not using SCM generator"))
                continue
            
            # Extract template data
            template_data = extract_template_fields(appset)
            applications_data.append(template_data)
            
            console.print(f"  [green]✓ Extracted: {template_data['name']}[/green]")
            
            # Transform to Git generator
            transformed_appset = transform_to_git_generator(
                appset,
                json_path_in_repo,
                config_repo_url
            )
            
            processed_files.append((yaml_file, transformed_appset))
            
        except Exception as e:
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
            errors.append((yaml_file.name, str(e)))
    
    # Display summary
    console.print("\n[bold]Migration Summary[/bold]")
    console.print(f"  Processed: {len(processed_files)}")
    console.print(f"  Skipped: {len(skipped_files)}")
    console.print(f"  Errors: {len(errors)}")
    
    if skipped_files:
        console.print("\n[yellow]Skipped Files:[/yellow]")
        for filename, reason in skipped_files:
            console.print(f"  • {filename}: {reason}")
    
    if errors:
        console.print("\n[red]Errors:[/red]")
        for filename, error in errors:
            console.print(f"  • {filename}: {error}")
    
    if not applications_data:
        console.print("\n[yellow]No ApplicationSets were processed. Exiting.[/yellow]")
        raise typer.Exit(0)
    
    # Preview extracted data
    console.print("\n[bold]Extracted Application Data:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name")
    table.add_column("Project")
    table.add_column("Path")
    table.add_column("Repo")
    
    for app in applications_data:
        table.add_row(
            app['name'],
            app['project'],
            app['path'],
            app['repoUrl']
        )
    
    console.print(table)
    
    if dry_run:
        console.print("\n[yellow]DRY RUN: No files will be written[/yellow]")
        console.print(f"\nWould create:")
        console.print(f"  • JSON data file: {json_output}")
        console.print(f"  • Transformed ApplicationSets in: {output_dir}")
        if create_pr:
            console.print(f"  • Branch: {branch_name}")
            console.print(f"  • Pull Request to: {target_branch}")
        raise typer.Exit(0)
    
    # Prepare file contents
    json_content = json.dumps({'applications': applications_data}, indent=2)
    
    transformed_yamls = {}
    for yaml_file, transformed_appset in processed_files:
        yaml_content = yaml.dump(transformed_appset, default_flow_style=False, sort_keys=False)
        transformed_yamls[yaml_file.name] = yaml_content
    
    # Create PR if requested
    if create_pr:
        console.print("\n[bold cyan]Creating Azure DevOps Pull Request...[/bold cyan]")
        
        try:
            ado_client = AzureDevOpsClient(ado_org, ado_pat, ado_project, ado_repo)
            
            # Check if branch exists, create if not
            if ado_client.branch_exists(branch_name):
                console.print(f"[yellow]⚠ Branch {branch_name} already exists, using existing branch[/yellow]")
            else:
                ado_client.create_branch(branch_name, target_branch)
            
            # Prepare files for commit
            files_to_commit = {}
            
            # Add JSON file
            files_to_commit[json_path_in_repo] = json_content
            
            # Add transformed ApplicationSets
            for filename, content in transformed_yamls.items():
                file_path = f"{appsets_path_in_repo}/{filename}"
                files_to_commit[file_path] = content
            
            # Commit files
            commit_message = f"Migrate ApplicationSets from SCM to Git generators\n\n"
            commit_message += f"- Migrated {len(processed_files)} ApplicationSet(s)\n"
            commit_message += f"- Created JSON data structure at {json_path_in_repo}\n"
            commit_message += f"- Transformed ApplicationSets use Git generator pattern"
            
            ado_client.commit_files(branch_name, files_to_commit, commit_message)
            
            # Create PR
            if pr_title is None:
                pr_title = f"Migrate ApplicationSets from SCM to Git generators ({len(processed_files)} apps)"
            
            if pr_description is None:
                pr_description = f"""## ApplicationSet Migration

This PR migrates ApplicationSets from SCM generators to Git generators with a JSON data structure.

### Changes
- **Migrated ApplicationSets**: {len(processed_files)}
- **JSON Data File**: `{json_path_in_repo}`
- **ApplicationSet Manifests**: `{appsets_path_in_repo}/`

### Migration Details
"""
                for app in applications_data:
                    pr_description += f"- `{app['name']}` (project: `{app['project']}`)\n"
                
                pr_description += f"""
### Testing Checklist
- [ ] Review JSON data structure in `{json_path_in_repo}`
- [ ] Verify transformed ApplicationSet manifests
- [ ] Validate Git generator configuration references correct repo
- [ ] Test ApplicationSet sync in development environment
- [ ] Confirm all applications are properly templated

### Rollback Plan
If issues arise, revert this PR and redeploy the original SCM-based ApplicationSets.
"""
            
            pr_id = ado_client.create_pull_request(
                source_branch=branch_name,
                target_branch=target_branch,
                title=pr_title,
                description=pr_description
            )
            
            console.print(f"\n[bold green]✓ Pull Request created successfully![/bold green]")
            console.print(f"\nPR Details:")
            console.print(f"  • PR ID: #{pr_id}")
            console.print(f"  • Branch: {branch_name} → {target_branch}")
            console.print(f"  • Files: {len(files_to_commit)}")
            
        except Exception as e:
            console.print(f"\n[red]✗ Error creating PR: {str(e)}[/red]")
            console.print("[yellow]Falling back to local file creation...[/yellow]")
            create_pr = False
    
    # Write files locally if not creating PR or if PR creation failed
    if not create_pr:
        # Write JSON data file
        json_output.parent.mkdir(parents=True, exist_ok=True)
        with open(json_output, 'w') as f:
            f.write(json_content)
        
        console.print(f"\n[green]✓ Created JSON data file: {json_output}[/green]")
        
        # Write transformed ApplicationSets
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for yaml_file, transformed_appset in processed_files:
            output_file = output_dir / yaml_file.name
            with open(output_file, 'w') as f:
                yaml.dump(transformed_appset, f, default_flow_style=False, sort_keys=False)
            console.print(f"[green]✓ Created: {output_file}[/green]")
        
        console.print(f"\n[bold green]Migration complete![/bold green]")
        console.print(f"\nNext steps:")
        console.print(f"  1. Review transformed ApplicationSets in: {output_dir}")
        console.print(f"  2. Commit {json_output} to {config_repo_url}")
        console.print(f"  3. Ensure JSON file is at path: {json_path_in_repo}")
        console.print(f"  4. Apply transformed ApplicationSets to your cluster")


@app.command()
def validate(
    input_dir: Path = typer.Argument(
        ...,
        help="Directory containing ApplicationSet YAML files",
        exists=True,
        file_okay=False,
        dir_okay=True
    )
):
    """
    Validate ApplicationSet YAML files and show which ones use SCM generators.
    """
    
    yaml_files = list(input_dir.glob("*.yaml")) + list(input_dir.glob("*.yml"))
    
    if not yaml_files:
        console.print(f"[yellow]No YAML files found in {input_dir}[/yellow]")
        raise typer.Exit(1)
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("File")
    table.add_column("Kind")
    table.add_column("Uses SCM")
    table.add_column("Template Name")
    
    for yaml_file in yaml_files:
        try:
            appset = load_applicationset(yaml_file)
            kind = appset.get('kind', 'Unknown')
            uses_scm = "✓" if is_scm_generator(appset) else "✗"
            
            try:
                template_data = extract_template_fields(appset)
                template_name = template_data['name']
            except:
                template_name = "N/A"
            
            table.add_row(yaml_file.name, kind, uses_scm, template_name)
            
        except Exception as e:
            table.add_row(yaml_file.name, "Error", "?", str(e))
    
    console.print(table)


if __name__ == "__main__":
    app()
