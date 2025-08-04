#!/usr/bin/env python3
"""
Community Management Script for MCP Context Manager

This script helps manage community engagement, track contributions,
and generate reports for the open source project.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.table import Table

console = Console()


class CommunityManager:
    """Manages community engagement and contribution tracking."""

    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.repo_owner = "yourusername"  # Update with your username
        self.repo_name = "mcp-context-manager-python"
        self.api_base = "https://api.github.com"

    def get_github_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "MCP-Context-Manager-Community",
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        return headers

    def get_contributors(self) -> List[Dict]:
        """Get list of contributors from GitHub API."""
        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/contributors"
        response = requests.get(url, headers=self.get_github_headers())

        if response.status_code == 200:
            return response.json()
        else:
            console.print(
                f"[red]Error fetching contributors: {response.status_code}[/red]"
            )
            return []

    def get_issues(
        self, state: str = "open", labels: Optional[List[str]] = None
    ) -> List[Dict]:
        """Get issues from GitHub API."""
        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/issues"
        params = {"state": state}
        if labels:
            params["labels"] = ",".join(labels)

        response = requests.get(url, headers=self.get_github_headers(), params=params)

        if response.status_code == 200:
            return response.json()
        else:
            console.print(f"[red]Error fetching issues: {response.status_code}[/red]")
            return []

    def get_pull_requests(self, state: str = "open") -> List[Dict]:
        """Get pull requests from GitHub API."""
        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/pulls"
        params = {"state": state}

        response = requests.get(url, headers=self.get_github_headers(), params=params)

        if response.status_code == 200:
            return response.json()
        else:
            console.print(f"[red]Error fetching PRs: {response.status_code}[/red]")
            return []

    def generate_community_report(self) -> None:
        """Generate a comprehensive community report."""
        console.print(
            Panel.fit("🧠 MCP Context Manager - Community Report", style="bold blue")
        )

        # Get data
        contributors = self.get_contributors()
        open_issues = self.get_issues("open")
        closed_issues = self.get_issues("closed")
        open_prs = self.get_pull_requests("open")
        closed_prs = self.get_pull_requests("closed")

        # Create tables
        self._display_contributors_table(contributors)
        self._display_issues_table(open_issues, "Open Issues")
        self._display_issues_table(closed_issues, "Recently Closed Issues")
        self._display_prs_table(open_prs, "Open Pull Requests")

        # Generate insights
        self._generate_insights(contributors, open_issues, open_prs)

    def _display_contributors_table(self, contributors: List[Dict]) -> None:
        """Display contributors in a table."""
        table = Table(title="👥 Contributors")
        table.add_column("Rank", style="cyan")
        table.add_column("Username", style="green")
        table.add_column("Contributions", style="yellow")
        table.add_column("Profile", style="blue")

        for i, contributor in enumerate(contributors[:10], 1):
            table.add_row(
                str(i),
                contributor["login"],
                str(contributor["contributions"]),
                contributor["html_url"],
            )

        console.print(table)

    def _display_issues_table(self, issues: List[Dict], title: str) -> None:
        """Display issues in a table."""
        if not issues:
            return

        table = Table(title=f"📋 {title}")
        table.add_column("Number", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Author", style="yellow")
        table.add_column("Labels", style="blue")
        table.add_column("Created", style="magenta")

        for issue in issues[:5]:  # Show top 5
            labels = ", ".join([label["name"] for label in issue.get("labels", [])])
            created = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
            created_str = created.strftime("%Y-%m-%d")

            table.add_row(
                f"#{issue['number']}",
                issue["title"][:50] + "..."
                if len(issue["title"]) > 50
                else issue["title"],
                issue["user"]["login"],
                labels,
                created_str,
            )

        console.print(table)

    def _display_prs_table(self, prs: List[Dict], title: str) -> None:
        """Display pull requests in a table."""
        if not prs:
            return

        table = Table(title=f"🔀 {title}")
        table.add_column("Number", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Author", style="yellow")
        table.add_column("Status", style="blue")
        table.add_column("Created", style="magenta")

        for pr in prs[:5]:  # Show top 5
            created = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
            created_str = created.strftime("%Y-%m-%d")

            table.add_row(
                f"#{pr['number']}",
                pr["title"][:50] + "..." if len(pr["title"]) > 50 else pr["title"],
                pr["user"]["login"],
                pr["state"],
                created_str,
            )

        console.print(table)

    def _generate_insights(
        self, contributors: List[Dict], issues: List[Dict], prs: List[Dict]
    ) -> None:
        """Generate community insights."""
        console.print("\n[bold]📊 Community Insights[/bold]")

        # Contributor insights
        total_contributors = len(contributors)
        top_contributor = contributors[0] if contributors else None

        console.print(f"👥 Total Contributors: {total_contributors}")
        if top_contributor:
            console.print(
                f"🏆 Top Contributor: {top_contributor['login']} ({top_contributor['contributions']} contributions)"
            )

        # Issue insights
        good_first_issues = [
            i
            for i in issues
            if any(label["name"] == "good first issue" for label in i.get("labels", []))
        ]
        help_wanted_issues = [
            i
            for i in issues
            if any(label["name"] == "help wanted" for label in i.get("labels", []))
        ]

        console.print(f"🎯 Good First Issues: {len(good_first_issues)}")
        console.print(f"🤝 Help Wanted Issues: {len(help_wanted_issues)}")
        console.print(f"🔀 Open Pull Requests: {len(prs)}")

        # Recommendations
        self._generate_recommendations(contributors, issues, prs)

    def _generate_recommendations(
        self, contributors: List[Dict], issues: List[Dict], prs: List[Dict]
    ) -> None:
        """Generate recommendations for community growth."""
        console.print("\n[bold]💡 Recommendations[/bold]")

        if len(contributors) < 10:
            console.print("🌱 Focus on attracting new contributors")
            console.print("   - Create more 'good first issue' labels")
            console.print("   - Improve onboarding documentation")
            console.print("   - Host community events or hackathons")

        if len(prs) > 5:
            console.print("⚡ Need more code review capacity")
            console.print("   - Recruit additional maintainers")
            console.print("   - Set up automated review processes")
            console.print("   - Create review guidelines")

        if len(issues) > 20:
            console.print("📋 High issue volume - consider triage")
            console.print("   - Set up issue templates")
            console.print("   - Create issue labels for categorization")
            console.print("   - Establish response time expectations")

    def create_welcome_message(self, contributor: Dict) -> str:
        """Create a personalized welcome message for new contributors."""
        return f"""
🎉 Welcome to the MCP Context Manager community, @{contributor['login']}!

Thank you for your contribution! We're excited to have you join our mission to build the future of AI memory management.

🧠 **What we're building**: A brain-like memory system for AI agents that learns and grows over time.

📚 **Getting Started**:
- Check out our [Contributing Guide](CONTRIBUTING.md)
- Browse [good first issues](https://github.com/{self.repo_owner}/{self.repo_name}/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
- Join our [Discussions](https://github.com/{self.repo_owner}/{self.repo_name}/discussions)

🤝 **Community Support**:
- Ask questions in Discussions
- Request code reviews early
- Don't hesitate to ask for help!

We believe every contribution, no matter how small, makes a difference. Thank you for being part of our journey! 🧠✨
"""

    def track_contributor_journey(self, username: str) -> Dict:
        """Track a contributor's journey through the project."""
        # This would integrate with your memory system to track contributor progress
        return {
            "username": username,
            "first_contribution": datetime.now().isoformat(),
            "contribution_types": [],
            "mentorship_needed": True,
            "ready_for_maintainer": False,
        }


def main():
    """Main function for community management."""
    if len(sys.argv) < 2:
        console.print("[red]Usage: python community_manager.py <command>[/red]")
        console.print("Commands: report, welcome <username>, track <username>")
        return

    command = sys.argv[1]
    manager = CommunityManager()

    if command == "report":
        manager.generate_community_report()
    elif command == "welcome" and len(sys.argv) > 2:
        username = sys.argv[2]
        welcome_msg = manager.create_welcome_message({"login": username})
        console.print(Panel(welcome_msg, title="Welcome Message"))
    elif command == "track" and len(sys.argv) > 2:
        username = sys.argv[2]
        journey = manager.track_contributor_journey(username)
        console.print(Panel(json.dumps(journey, indent=2), title="Contributor Journey"))
    else:
        console.print("[red]Invalid command or missing arguments[/red]")


if __name__ == "__main__":
    main()
