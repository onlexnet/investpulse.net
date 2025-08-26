terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 2.0"
    }
  }
}

provider "azurerm" {
  features {}
}

module "resource_group" {
  source = "../"
  resource_group_location = "westeurope"
}

output "resource_group_name" {
  value = module.resource_group.azurerm_resource_group_investpulse_net.name
}
