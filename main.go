package main

import (
	"context"
	"log"

	"github.com/hashicorp/terraform-plugin-framework/providerserver"
	"terraform-mssql-provider/internal/provider"
)

func main() {
	err := providerserver.Serve(context.Background(), mssql.NewProvider, providerserver.ServeOpts{
		Address: "registry.terraform.io/local/mssql",
	})
	if err != nil {
		log.Fatal(err)
	}
}
