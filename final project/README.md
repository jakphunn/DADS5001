This is our group project for DADS5001: Tools for machine learning

We want to fix the pain points about customer services in home service segment.
The pain points are the miscommunication between our moderators and the clients, and insufficient domain knowledge to interpret the true problems of our client reports.

![3](https://github.com/jakphunn/DADS5001/assets/99724047/38c52ce0-0cac-43e7-9649-c54a2759e39c)


Clients will report us what are the issues happening in their property via website, our API will do text classification which categories it should be labelled.

Our categories are the departments in our home services company:
1. Electrical
2. Waterworks
3. Structural
4. Arborist
5. Pesticide Control

![10](https://github.com/jakphunn/DADS5001/assets/99724047/47af713a-6c7e-4f4c-bf1a-abe2e96ba972)


So we decided to use LLM API we found on Huggingface for helping us fixing those pain points.

Our application pipeline starts with taking the text input from clients into language detection API to detect which language it is. Second, it will be send into translator API to translate the text into english. Third, put the english translated text into zero-shot text classification API. then it will be saved into our database on PostgreSQL then displaying them on the dashboard, the managers of each department will use the information to assign the tasks for the teams.

This is our application pipeline:

![15](https://github.com/jakphunn/DADS5001/assets/99724047/ba8ee9d2-5c72-406f-987d-19f5332eb771)


This is a demo of our home service website:
![11](https://github.com/jakphunn/DADS5001/assets/99724047/3c2ddff5-261d-4e5f-8e26-1d4e7cd10bdf)
![12](https://github.com/jakphunn/DADS5001/assets/99724047/af1198b7-0371-44f7-be2c-abb8d0efcc0a)


Since our service will mainly operate in North America, our application will be able to work on 4 languages: English, Spanish, German, and French.

![5](https://github.com/jakphunn/DADS5001/assets/99724047/b5755b88-7de0-4869-af82-8262c0175781)
![6](https://github.com/jakphunn/DADS5001/assets/99724047/45a959a1-e4cb-4d44-99f9-9d95b1bff753)
![7](https://github.com/jakphunn/DADS5001/assets/99724047/3dd15ebd-d70b-4a2d-a4bf-87bee0ce9dfc)
![8](https://github.com/jakphunn/DADS5001/assets/99724047/0b5a1b7b-f2dd-432c-8216-2fd6642980ed)


This is the example of how our API output:

![9](https://github.com/jakphunn/DADS5001/assets/99724047/56eab422-acfb-4b5d-904b-24ff9ff64114)


This is a demo for our dashboard:

![14](https://github.com/jakphunn/DADS5001/assets/99724047/a29899fe-2761-48d5-ab56-603917cfb1b8)

Group member:
Jakphun Nimthong 6610412008
Ranakorn Boonsuankergchai 6610412003
Pattaradanai Lirdkittisakul 6610412011
