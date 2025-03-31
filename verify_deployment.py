#!/usr/bin/env python3
"""
Deployment Verification Script for Anatomy Study App
This script validates that the application is ready for cloud deployment
by checking required files, directories, and configuration consistency.
"""

import os
import sys
import json
import importlib.util
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deployment_verification.log')
    ]
)
logger = logging.getLogger('verify_deployment')

class DeploymentVerifier:
    def __init__(self):
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.results = {
            "verification_time": "",
            "overall_status": "NOT VERIFIED",
            "entry_point_check": False,
            "directory_check": False,
            "config_check": False,
            "dependency_check": False,
            "image_resource_check": False,
            "content_check": False,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
    def verify_all(self):
        """Run all verification checks"""
        from datetime import datetime
        self.results["verification_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Run all checks
            self.verify_entry_point()
            self.verify_directories()
            self.verify_configurations()
            self.verify_dependencies()
            self.verify_image_resources()
            self.verify_content()
            
            # Determine overall status
            if not self.results["errors"]:
                if not self.results["warnings"]:
                    self.results["overall_status"] = "READY FOR DEPLOYMENT"
                else:
                    self.results["overall_status"] = "READY WITH WARNINGS"
            else:
                self.results["overall_status"] = "NOT READY - ERRORS FOUND"
                
            return self.results
            
        except Exception as e:
            logger.error(f"Verification process failed: {str(e)}")
            self.results["errors"].append(f"Verification process error: {str(e)}")
            self.results["overall_status"] = "VERIFICATION FAILED"
            return self.results
    
    def verify_entry_point(self):
        """Verify the main entry point exists and can be imported"""
        logger.info("Checking entry point...")
        
        entry_point = "cloud_deploy_app_main.py"
        entry_path = os.path.join(self.app_dir, entry_point)
        
        if not os.path.exists(entry_path):
            logger.error(f"Entry point {entry_point} not found")
            self.results["errors"].append(f"Missing entry point: {entry_point}")
            return False
        
        # Try to import the module without executing it
        try:
            spec = importlib.util.spec_from_file_location("cloud_deploy_app_main", entry_path)
            module = importlib.util.module_from_spec(spec)
            logger.info(f"Entry point {entry_point} found and valid")
            self.results["entry_point_check"] = True
        except Exception as e:
            logger.error(f"Entry point import error: {str(e)}")
            self.results["errors"].append(f"Entry point import error: {str(e)}")
            return False
        
        return True
    
    def verify_directories(self):
        """Verify all required directories exist"""
        logger.info("Checking required directories...")
        
        # Import the ensure_directories_exist function
        try:
            from image_utils import ensure_directories_exist
            if ensure_directories_exist():
                logger.info("All required directories exist or were created")
                self.results["directory_check"] = True
                return True
            else:
                logger.error("Failed to verify all required directories")
                self.results["errors"].append("Failed to verify required directories")
                return False
        except ImportError:
            logger.error("Failed to import image_utils module")
            self.results["errors"].append("Missing image_utils module")
            return False
    
    def verify_configurations(self):
        """Verify deployment configuration files are consistent"""
        logger.info("Checking deployment configurations...")
        
        config_files = {
            "vercel.json": "cloud_deploy_app_main.py",
            "Procfile": "cloud_deploy_app_main.py",
            "render.yaml": "cloud_deploy_app_main.py"
        }
        
        success = True
        
        for config_file, expected_entry in config_files.items():
            config_path = os.path.join(self.app_dir, config_file)
            
            if not os.path.exists(config_path):
                logger.warning(f"Configuration file {config_file} not found")
                self.results["warnings"].append(f"Missing configuration file: {config_file}")
                success = False
                continue
            
            try:
                if config_file == "vercel.json":
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    if "builds" in config and len(config["builds"]) > 0:
                        if config["builds"][0].get("src") != expected_entry:
                            logger.error(f"{config_file} points to incorrect entry point: {config['builds'][0].get('src')}")
                            self.results["errors"].append(f"{config_file} has incorrect entry point")
                            success = False
                
                elif config_file == "Procfile":
                    with open(config_path, 'r') as f:
                        content = f.read()
                    if expected_entry not in content:
                        logger.error(f"{config_file} does not reference the correct entry point")
                        self.results["errors"].append(f"{config_file} has incorrect entry point")
                        success = False
                
                elif config_file == "render.yaml":
                    with open(config_path, 'r') as f:
                        try:
                            import yaml
                            config = yaml.safe_load(f)
                            
                            if "services" in config and len(config["services"]) > 0:
                                if expected_entry not in config["services"][0].get("startCommand", ""):
                                    logger.error(f"{config_file} does not reference the correct entry point")
                                    self.results["errors"].append(f"{config_file} has incorrect entry point")
                                    success = False
                        except:
                            # If yaml is not available, use a simple string check
                            f.seek(0)
                            content = f.read()
                            if expected_entry not in content:
                                logger.error(f"{config_file} does not reference the correct entry point")
                                self.results["errors"].append(f"{config_file} has incorrect entry point")
                                success = False
            
            except Exception as e:
                logger.error(f"Error checking {config_file}: {str(e)}")
                self.results["errors"].append(f"Config verification error for {config_file}: {str(e)}")
                success = False
        
        self.results["config_check"] = success
        return success
    
    def verify_dependencies(self):
        """Verify requirements.txt has valid dependencies"""
        logger.info("Checking dependencies...")
        
        req_path = os.path.join(self.app_dir, "requirements.txt")
        
        if not os.path.exists(req_path):
            logger.error("requirements.txt not found")
            self.results["errors"].append("Missing requirements.txt")
            return False
        
        try:
            with open(req_path, 'r') as f:
                content = f.read()
            
            # Check for key dependencies
            required_packages = ["streamlit", "pandas", "nltk", "pillow", "matplotlib"]
            missing_packages = []
            
            for package in required_packages:
                if package.lower() not in content.lower():
                    missing_packages.append(package)
            
            if missing_packages:
                logger.error(f"Missing required packages in requirements.txt: {', '.join(missing_packages)}")
                self.results["errors"].append(f"Missing dependencies: {', '.join(missing_packages)}")
                return False
            
            # Check for future-dated dependencies
            future_packages = []
            for line in content.split('\n'):
                if line.strip() and '==' in line and not line.strip().startswith('#'):
                    package, version = line.split('==', 1)
                    if version.startswith('202'):  # Check for year format
                        year = int(version.split('.')[0])
                        if year > 2023:  # Current year is 2023
                            future_packages.append(f"{package} ({version})")
            
            if future_packages:
                logger.warning(f"Found future-dated package versions: {', '.join(future_packages)}")
                self.results["warnings"].append(f"Future-dated packages: {', '.join(future_packages)}")
            
            logger.info("Dependencies check passed")
            self.results["dependency_check"] = True
            return True
            
        except Exception as e:
            logger.error(f"Error checking dependencies: {str(e)}")
            self.results["errors"].append(f"Dependency verification error: {str(e)}")
            return False
    
    def verify_image_resources(self):
        """Verify image resources are available or can be generated"""
        logger.info("Checking image resources...")
        
        try:
            # Import the validation function
            from image_utils import validate_image_resources
            validation_results = validate_image_resources()
            
            if validation_results["success"]:
                logger.info("Image resource check passed")
                self.results["image_resource_check"] = True
                
                # Add warnings for missing images that were auto-generated
                systems = ["lymphatic", "respiratory", "digestive"]
                expected_counts = {
                    "lymphatic": 3,  # thymus, lymph_node, spleen
                    "respiratory": 2,  # trachea, lung
                    "digestive": 2    # esophagus_stomach, small_intestine
                }
                
                for system in systems:
                    found_count = len(validation_results["histology_images"][system])
                    expected = expected_counts.get(system, 0)
                    
                    if found_count < expected:
                        logger.warning(f"Some {system} histology images are placeholder generated")
                        self.results["warnings"].append(f"Using {expected - found_count} placeholder images for {system}")
                
                return True
            else:
                logger.error("Image resource validation failed")
                for error in validation_results.get("errors", []):
                    self.results["errors"].append(f"Image resource error: {error}")
                return False
                
        except ImportError:
            logger.error("Failed to import image_utils module")
            self.results["errors"].append("Missing image_utils module")
            return False
    
    def verify_content(self):
        """Verify study content files exist and are readable"""
        logger.info("Checking study content...")
        
        knowledge_dir = os.path.join(self.app_dir, "data", "knowledge")
        systems = ["lymphatic", "respiratory", "digestive"]
        
        if not os.path.exists(knowledge_dir):
            logger.error(f"Knowledge directory not found: {knowledge_dir}")
            self.results["errors"].append("Missing knowledge directory")
            return False
        
        missing_content = []
        
        for system in systems:
            content_file = os.path.join(knowledge_dir, f"{system}.html")
            if not os.path.exists(content_file):
                missing_content.append(system)
                continue
                
            # Check if file is readable and has content
            try:
                with open(content_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if len(content) < 100:  # Arbitrary threshold for minimal content
                    logger.warning(f"{system}.html appears to be empty or too small")
                    self.results["warnings"].append(f"{system}.html may have insufficient content")
            except Exception as e:
                logger.error(f"Error reading {system}.html: {str(e)}")
                self.results["errors"].append(f"Content file error: {system}.html - {str(e)}")
        
        if missing_content:
            logger.error(f"Missing content files: {', '.join(missing_content)}")
            self.results["errors"].append(f"Missing content files: {', '.join(missing_content)}")
            return False
        
        # Check for quiz data
        quiz_file = os.path.join(self.app_dir, "data", "enhanced_quizzes.json")
        if not os.path.exists(quiz_file):
            logger.error(f"Quiz data file not found: {quiz_file}")
            self.results["errors"].append("Missing quiz data file")
            return False
        
        logger.info("Content check passed")
        self.results["content_check"] = True
        return True
    
    def print_results(self):
        """Print verification results in a readable format"""
        print("\n" + "="*80)
        print(f"ANATOMY STUDY APP DEPLOYMENT VERIFICATION")
        print(f"Verification Time: {self.results['verification_time']}")
        print("="*80)
        
        print(f"\nOVERALL STATUS: {self.results['overall_status']}")
        
        print("\nCHECKS:")
        print(f"  ✓ Entry Point Check: {'PASSED' if self.results['entry_point_check'] else 'FAILED'}")
        print(f"  ✓ Directory Check: {'PASSED' if self.results['directory_check'] else 'FAILED'}")
        print(f"  ✓ Configuration Check: {'PASSED' if self.results['config_check'] else 'FAILED'}")
        print(f"  ✓ Dependency Check: {'PASSED' if self.results['dependency_check'] else 'FAILED'}")
        print(f"  ✓ Image Resource Check: {'PASSED' if self.results['image_resource_check'] else 'FAILED'}")
        print(f"  ✓ Content Check: {'PASSED' if self.results['content_check'] else 'FAILED'}")
        
        if self.results["errors"]:
            print("\nERRORS:")
            for error in self.results["errors"]:
                print(f"  ✗ {error}")
        
        if self.results["warnings"]:
            print("\nWARNINGS:")
            for warning in self.results["warnings"]:
                print(f"  ! {warning}")
        
        if self.results["recommendations"]:
            print("\nRECOMMENDATIONS:")
            for rec in self.results["recommendations"]:
                print(f"  • {rec}")
        
        print("\n" + "="*80)
        
        # Provide summary based on status
        if self.results["overall_status"] == "READY FOR DEPLOYMENT":
            print("The application is ready for deployment! All checks passed successfully.")
        elif self.results["overall_status"] == "READY WITH WARNINGS":
            print("The application can be deployed, but consider addressing the warnings first.")
        else:
            print("The application is NOT ready for deployment. Please fix the errors listed above.")
        
        print("="*80 + "\n")

if __name__ == "__main__":
    verifier = DeploymentVerifier()
    results = verifier.verify_all()
    verifier.print_results()
    
    # Exit with appropriate code for CI/CD pipelines
    sys.exit(0 if results["overall_status"] in ["READY FOR DEPLOYMENT", "READY WITH WARNINGS"] else 1)
