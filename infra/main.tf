# Generate a random animal-line name for the resource group
resource "random_pet" "rg_name" {
	length    = 1
	separator = "-"
}

# Configure the Azure Provider
provider "azurerm" {
	features {}
	subscription_id = "ac0e7cdd-3111-4671-a602-0d93afb5df20" # dev-investpulse-net
}

# Create a resource group with --investpulse-net suffix
resource "azurerm_resource_group" "investpulse_net" {
	name     = "${random_pet.rg_name.id}-investpulse-net"
	location = var.resource_group_location
}
