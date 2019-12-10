import oci
import json
import logging

def StopInstances(instances, must_run):
    for instance in instances:
        response = ComputeClient.get_instance(instance.id)
        # Handle details for Compute Instances
        if response.data.lifecycle_state == "RUNNING":
            for running_instance in range(len(must_run)):
                # REPLACE with not equal
                if response.data.id != must_run[running_instance]:
                    ComputeClient.instance_action(response.data.id, "STOP")



if __name__ == "__main__":
    configfile = "C:\\workspace\\ociFunctions\\InstancesStop\\config"
    config = oci.config.from_file(configfile)

    # Get basic information of your tenancy, region, users, etc
    identity = oci.identity.IdentityClient(config)
    user = identity.get_user(config["user"]).data
    RootCompartmentID = user.compartment_id

    print("Logged in as: {} @ {}".format(user.description, config["region"]))
    # get tenancy name
    tenancy = identity.get_tenancy(config["tenancy"])
    tenancyName = tenancy.data
    print("Tenancy Name: {}".format(tenancyName.name))

    # get all availale regions
    print("Querying Enabled Regions:")
    response = identity.list_region_subscriptions(config["tenancy"])
    regions = response.data

    for region in regions:
        if region.is_home_region:
            home = "Home region"
        else:
            home = ""
        print("- {} ({}) {}".format(region.region_name, region.status, home))

    # Retrieve all instances for each config file (regions)
    for region in regions:
        print("Region name:{}".format(region.region_name))
        config = oci.config.from_file(configfile)
        config["region"] = region.region_name

        identity = oci.identity.IdentityClient(config)
        user = identity.get_user(config["user"]).data
        RootCompartmentID = user.compartment_id

        ComputeClient = oci.core.ComputeClient(config)
        NetworkClient = oci.core.VirtualNetworkClient(config)

        # Check instances for all the underlaying Compartments
        response = oci.pagination.list_call_get_all_results(identity.list_compartments, RootCompartmentID,
                                                            compartment_id_in_subtree=True)
        compartments = response.data

        # Insert (on top) the root compartment
        RootCompartment = oci.identity.models.Compartment()
        RootCompartment.id = RootCompartmentID
        RootCompartment.name = "root"
        RootCompartment.lifecycle_state = "ACTIVE"
        compartments.insert(0, RootCompartment)

        must_run = ["ocid1.instance.oc1.iad.1234",
                    "ocid1.instance.oc1.iad.5678"]

        for compartment in compartments:
            compartmentName = compartment.name
            # print ("Checking : " + compartment.name)
            if compartment.lifecycle_state == "ACTIVE":
                print("process Compartment:" + compartmentName)
                compartmentID = compartment.id
                # Compute instance
                try:
                    response = oci.pagination.list_call_get_all_results(ComputeClient.list_instances,compartment_id=compartmentID)
                    if len(response.data) > 0:
                        StopInstances(response.data, must_run)

                except Exception as e:
                    print("----------------- Error -------------------")
                    print(e)
                    print("-------------------End----------------------")


