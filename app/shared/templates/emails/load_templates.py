
from pathlib import Path
from typing import Dict, Any


class LoadTemplates:
    
    def __init__(self, templates_dir: str = None):
        current_dir = Path(__file__).parent
        self.templates_dir = Path(templates_dir) if templates_dir else current_dir
    
    def load_template(self, template_name: str) -> str:
        
        if not self.templates_dir:
            raise FileNotFoundError("Templates directory is not set")
    
        template_path = self.templates_dir / f"{template_name}.html"

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as file:
            return file.read()

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        template = self.load_template(template_name)
        
       
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            template = template.replace(placeholder, str(value))
        
        return template
    
    def render_welcome_email(self, full_name: str, email: str, username: str, tenant_id: str) -> str:
    
        context = {
            "full_name": full_name or username,
            "email": email,
            "username": username,
            "tenant_id": str(tenant_id)
        }
        return self.render_template("welcome", context)
    
    def render_profile_updated_email(self, changes: list, tenant_id: str, updated_at: str) -> str:
       
        changes_list = "".join([f"<li>{change}</li>" for change in changes])
        
        context = {
            "changes_list": changes_list,
            "tenant_id": str(tenant_id),
            "updated_at": updated_at
        }
        return self.render_template("profile_updated", context)
