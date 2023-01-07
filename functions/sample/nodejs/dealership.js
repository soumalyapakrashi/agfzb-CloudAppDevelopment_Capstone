/**
  *
  * main() will be run when you invoke this action
  *
  * @param Cloud Functions actions accept a single parameter, which must be a JSON object.
  *
  * @return The output of this action, which must be a JSON object.
  *
  * This is the final version which is used in Cloud Functions
  * 
  */

const { CloudantV1 } = require('@ibm-cloud/cloudant');
const { IamAuthenticator } = require('ibm-cloud-sdk-core');

async function main(params) {
    let docs = undefined;
    
    try {
        // Create a new authenticator instance for IAM authentication. This API key is obtained from Cloudant credentials
        // Replace the {{CLOUDANT_API_KEY}} with the actual API key (or some environment variable)
        const authenticator = new IamAuthenticator({ apikey: '{{CLOUDANT_API_KEY}}' })
        
        // Create a new instance of Cloudant with the authenticator details from above
        const cloudant = CloudantV1.newInstance({
            authenticator: authenticator
        });
        
        // Set the URL in which the particular cloudant instance will be receiving requests
        // Replace the {{CLOUDANT_SERVICE_URL}} with the actual endpoint URL (or env variable)
        cloudant.setServiceUrl('{{CLOUDANT_SERVICE_URL}}');
        
        // Get all the documents from the 'dealerships' database
        docs = await cloudant.postAllDocs({
            db: 'dealerships',
            includeDocs: true
        });
        
        // Re-structure the data as required
        docs = docs["result"]["rows"].map(doc => doc["doc"])
        
        // Drop the _id and _rev entries as these are not required by clients
        docs.forEach(doc => {
            delete doc["_id"];
            delete doc["_rev"];
        });
    }
    catch(error) {
        return {
            statusCode: 500,
            headers: { 'Content-Type': 'application/json' },
            body: error.description
        };
    }
    
    // If state query parameter is provided, return only the documents of that state
    if(params.state) {
        // Filter out the documents of the particular state
        let filtered_docs = docs.filter(doc => doc["state"] == params.state)
        
        // If no result is found, return error
        if(filtered_docs.length == 0) {
            return {
                statusCode: 404,
                headers: { 'Content-Type': 'application/json' },
                body: `No result found for state ${params.state}`
            }
        }
        else {
            return {
                statusCode: 200,
                headers: { 'Content-Type': 'application/json' },
                body: filtered_docs
            };
        }
    }
    
    // If no state query parameter is mentioned
    else {
        // If no data in the database
        if(docs.length == 0) {
            return {
                statusCode: 404,
                headers: { 'Content-Type': 'application/json' },
                body: `No entry in database`
            };
        }
        else {
            return {
                statusCode: 200,
                headers: { 'Content-Type': 'application/json' },
                body: docs
            };
        }
    }
}
