"""LICENSE file generator"""
from datetime import datetime
from core.decorators import Generator
from ..templates.base import BaseTemplateGenerator


@Generator(
    category="config",
    priority=4,
    description="Generate LICENSE file with MIT license"
)
class LicenseGenerator(BaseTemplateGenerator):
    """LICENSE File generator"""
    
    def generate(self) -> None:
        """Generate LICENSE file"""
        project_name = self.config_reader.get_project_name()
        current_year = datetime.now().year
        
        content = self._build_mit_license(project_name, current_year)
        
        self.file_ops.create_file(
            file_path="LICENSE",
            content=content,
            overwrite=True
        )
    
    def _build_mit_license(self, project_name: str, year: int) -> str:
        """Build MIT license content"""
        return f'''MIT License

Copyright (c) {year} {project_name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''