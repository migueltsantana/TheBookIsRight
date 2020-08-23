import json
import os
import sys
import time
import zipfile

import botocore
import tabulate
import typer
import boto3

from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, CRON

app = typer.Typer()


@app.command()
def add_book(isbn: int = typer.Option(..., prompt="What is the book's ISBN?", help="The ISBN-13 of the book you want "
                                                                                   "to track"),
             bookstore: str = typer.Option(..., prompt="What is the bookstore?", help="The name of the bookstore"),
             url: str = typer.Option(..., prompt="What is the URL I should watch?", help="The url of the book in the "
                                                                                         "bookstore")):
    """
    Add a book to be tracked
    """
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )
    try:
        session.resource("dynamodb").Table("books_to_watch").put_item(
            Item={
                "isbn": isbn,
                "bookstore": bookstore,
                "url": url,
                "watch_status": True
            }
        )
        typer.secho(f"Book with ISBN {isbn} from {bookstore} created successfully!", fg=typer.colors.GREEN, bold=True)
    except botocore.exceptions.ClientError as err:
        typer.echo(typer.style(err.response["Error"]["Message"], fg=typer.colors.RED, bold=True))
        raise typer.Exit()


@app.command()
def list_books():
    """
    List all the books stored
    """
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )
    dataset = session.resource("dynamodb").Table("books_to_watch").scan()["Items"]
    header = dataset[0].keys()
    rows = [x.values() for x in dataset]
    typer.echo(tabulate.tabulate(rows, header, tablefmt='grid', floatfmt=".0f"))


@app.command()
def unwatch_book(isbn: int = typer.Option(..., prompt="What is the book's ISBN?", help="The ISBN-13 of the book you "
                                                                                       "want to track"),
                 bookstore: str = typer.Option(..., prompt="What is the bookstore?", help="The name of the bookstore")):
    """
    Stop watching the book's price
    """
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )
    try:
        session.resource("dynamodb").Table("books_to_watch").update_item(
            Key={
                'isbn': isbn,
                'bookstore': bookstore
            },
            UpdateExpression="set watch_status = :r",
            ExpressionAttributeValues={
                ':r': False
            },
            ReturnValues="UPDATED_NEW"
        )
        typer.secho(f"Book with ISBN {isbn} from {bookstore} updated successfully!", fg=typer.colors.GREEN, bold=True)
    except botocore.exceptions.ClientError as err:
        typer.echo(typer.style(err.response["Error"]["Message"], fg=typer.colors.RED, bold=True))
        raise typer.Exit()


@app.command()
def watch_book(isbn: int = typer.Option(..., prompt="What is the book's ISBN?", help="The ISBN-13 of the book you "
                                                                                     "want to track"),
               bookstore: str = typer.Option(..., prompt="What is the bookstore?", help="The name of the bookstore")):
    """
    Resume watching the book's price
    """
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )
    try:
        session.resource("dynamodb").Table("books_to_watch").update_item(
            Key={
                'isbn': isbn,
                'bookstore': bookstore
            },
            UpdateExpression="set watch_status = :r",
            ExpressionAttributeValues={
                ':r': True
            },
            ReturnValues="UPDATED_NEW"
        )
        typer.secho(f"Book with ISBN {isbn} from {bookstore} updated successfully!", fg=typer.colors.GREEN, bold=True)
    except botocore.exceptions.ClientError as err:
        typer.echo(typer.style(err.response["Error"]["Message"], fg=typer.colors.RED, bold=True))
        raise typer.Exit()


@app.command()
def delete_book(isbn: int = typer.Option(..., prompt="What is the book's ISBN?",
                                         help="The ISBN-13 of the book you want to track"),
                bookstore: str = typer.Option(..., prompt="What is the bookstore?", help="The name of the bookstore")):
    """
    Delete a book from the database
    """
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )
    try:
        session.resource("dynamodb").Table("books_to_watch").delete_item(
            Key={
                'isbn': isbn,
                'bookstore': bookstore
            }
        )
        typer.secho(f"Book with ISBN {isbn} from {bookstore} deleted successfully!", fg=typer.colors.GREEN, bold=True)
    except botocore.exceptions.ClientError as err:
        typer.echo(typer.style(err.response["Error"]["Message"], fg=typer.colors.RED, bold=True))
        raise typer.Exit()


@app.command()
def deploy():
    """
    Deploy the current installation to AWS
    """
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )

    dynamodb = session.resource('dynamodb')

    typer.echo(typer.style("Creating table 'books_to_watch'... Please wait as this may take a while.",
                           fg=typer.colors.BRIGHT_WHITE, bold=True))

    try:
        table = dynamodb.create_table(
            TableName='books_to_watch',
            KeySchema=[
                {
                    'AttributeName': 'isbn',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'bookstore',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'isbn',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'bookstore',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )

        table.meta.client.get_waiter('table_exists').wait(TableName='books_to_watch')

        typer.echo(typer.style("Table 'books_to_watch' created successfully!", fg=typer.colors.GREEN, bold=True))

    except botocore.exceptions.ClientError as err:
        typer.echo(typer.style(err.response["Error"]["Message"], fg=typer.colors.RED, bold=True))
        raise typer.Exit()

    typer.echo(typer.style("Creating table 'books_price_data'... Please wait as this may take a while.",
                           fg=typer.colors.BRIGHT_WHITE, bold=True))

    try:
        table = dynamodb.create_table(
            TableName='books_price_data',
            KeySchema=[
                {
                    'AttributeName': 'isbn',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'timestamp',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'isbn',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )

        table.meta.client.get_waiter('table_exists').wait(TableName='books_price_data')

        typer.echo(typer.style("Table 'books_price_data' created successfully!", fg=typer.colors.GREEN, bold=True))

    except botocore.exceptions.ClientError as err:
        typer.echo(typer.style(err.response["Error"]["Message"], fg=typer.colors.RED, bold=True))
        raise typer.Exit()

    iam = session.client('iam')

    role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": ["lambda.amazonaws.com", "events.amazonaws.com"]},
                "Action": "sts:AssumeRole"
            }
        ]
    }

    try:
        typer.echo(typer.style("Trying IAM role for the function...", fg=typer.colors.BRIGHT_WHITE, bold=True))
        role_response = iam.create_role(
            RoleName='LambdaTheBookIsRight',
            AssumeRolePolicyDocument=json.dumps(role_policy),
            Description='Lambda Function Role for The Book Is Right'
        )
        iam.attach_role_policy(
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
            RoleName='LambdaTheBookIsRight',
        )
        waiter = iam.get_waiter("role_exists")
        waiter.wait(
            RoleName='LambdaTheBookIsRight',
            WaiterConfig={
                'Delay': 100,
                'MaxAttempts': 100
            }
        )
        time.sleep(20)
        typer.echo(typer.style("Role created successfully!", fg=typer.colors.GREEN, bold=True))
    except botocore.exceptions.ClientError as err:
        typer.echo(typer.style(err.response["Error"]["Message"], fg=typer.colors.RED, bold=True))
        raise typer.Exit()

    typer.echo(typer.style("Zipping all the contents of the function...", fg=typer.colors.BRIGHT_WHITE, bold=True))

    zipf = zipfile.ZipFile('function.zip', 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
    for root, dirs, files in os.walk("."):
        if "venv" in dirs:
            dirs.remove("venv")
        for file in files:
            zipf.write(os.path.join(root, file))
    abs_src = os.path.abspath(f"venv/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages")
    for root, dirs, files in os.walk(f"venv/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"):
        for file in files:
            absname = os.path.abspath(os.path.join(root, file))
            arcname = absname[len(abs_src) + 1:]
            zipf.write(os.path.join(root, file), arcname)
    zipf.close()

    typer.echo(typer.style("Function zipped successfully!", fg=typer.colors.GREEN, bold=True))

    function = session.client('lambda')

    try:
        typer.echo(typer.style("Creating and publishing the function...", fg=typer.colors.BRIGHT_WHITE, bold=True))
        function_response = function.create_function(
            FunctionName='thebookisright',
            Runtime='python3.8',
            Role=role_response["Role"]["Arn"],
            Handler='lambda_function.lambda_handler',
            Code={
                'ZipFile': open("function.zip", 'rb').read()
            },
            Description='The right price for the right book! - Based on https://github.com/migueltsantana/TheBookIsRight',
            Timeout=900,
            MemorySize=1408,
            Publish=True
        )
        typer.echo(typer.style("Function published successfully!", fg=typer.colors.GREEN, bold=True))
    except botocore.exceptions.ClientError as err:
        typer.echo(typer.style(err.response["Error"]["Message"], fg=typer.colors.RED, bold=True))
        raise typer.Exit()

    try:
        typer.echo(typer.style("Creating the CloudWatch event...", fg=typer.colors.BRIGHT_WHITE, bold=True))
        session.client("events").put_rule(
            Name="TheBookIsRight",
            ScheduleExpression=f"cron({CRON})",
            State="ENABLED",
            Description="Trigger for The Book Is Right AWS Lambda function",
            RoleArn=role_response["Role"]["Arn"]
        )
        session.client("events").put_targets(
            Rule="TheBookIsRight",
            Targets=[
                {
                    "Id": function_response["FunctionName"],
                    "Arn": function_response["FunctionArn"]
                },
            ]
        )
        typer.echo(typer.style("CloudWatch event created successfully!", fg=typer.colors.GREEN, bold=True))

    except botocore.exceptions.ClientError as err:
        typer.echo(typer.style(err.response["Error"]["Message"], fg=typer.colors.RED, bold=True))
        raise typer.Exit()

@app.command()
def undeploy(abort_when_fail: bool = typer.Option(True, help="Stop if any exception is raised")):
    """
    Undeploy the current installation from AWS
    """
    reset = typer.confirm("Are you sure you want to PERMANENTLY DELETE ALL the resources from the cloud?", abort=True)
    if not reset:
        raise typer.Abort()

    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )

    try:
        typer.echo(typer.style("Deleting the table 'books_to_watch'...", fg=typer.colors.BRIGHT_WHITE, bold=True))
        session.client('dynamodb').delete_table(
            TableName='books_to_watch'
        )
        typer.echo(typer.style("Table 'books_to_watch' deleted successfully!", fg=typer.colors.GREEN, bold=True))
    except botocore.exceptions.ClientError as err:
        typer.echo(typer.style(f'ERROR: {err.response["Error"]["Message"]}', fg=typer.colors.RED, bold=True))
        if abort_when_fail: raise typer.Exit()

    try:
        typer.echo(typer.style("Deleting the table 'books_price_data'...", fg=typer.colors.BRIGHT_WHITE, bold=True))
        session.client('dynamodb').delete_table(
            TableName='books_price_data'
        )
        typer.echo(typer.style("Table 'books_price_data' deleted successfully!", fg=typer.colors.GREEN, bold=True))
    except botocore.exceptions.ClientError as err:
        typer.echo(typer.style(f'ERROR: {err.response["Error"]["Message"]}', fg=typer.colors.RED, bold=True))
        if abort_when_fail: raise typer.Exit()

    try:
        typer.echo(typer.style("Deleting the IAM role...", fg=typer.colors.BRIGHT_WHITE, bold=True))
        session.client('iam').detach_role_policy(
            RoleName='LambdaTheBookIsRight',
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        session.client('iam').delete_role(
            RoleName='LambdaTheBookIsRight'
        )
        typer.echo(typer.style("IAM role deleted successfully!", fg=typer.colors.GREEN, bold=True))
    except botocore.exceptions.ClientError as err:
        typer.echo(typer.style(f'ERROR: {err.response["Error"]["Message"]}', fg=typer.colors.RED, bold=True))
        if abort_when_fail: raise typer.Exit()

    try:
        typer.echo(typer.style("Deleting the Lambda function...", fg=typer.colors.BRIGHT_WHITE, bold=True))
        session.client('lambda').delete_function(
            FunctionName='thebookisright'
        )
        typer.echo(typer.style("Lambda function deleted successfully!", fg=typer.colors.GREEN, bold=True))
    except botocore.exceptions.ClientError as err:
        typer.echo(typer.style(f'ERROR: {err.response["Error"]["Message"]}', fg=typer.colors.RED, bold=True))
        if abort_when_fail: raise typer.Exit()

    try:
        typer.echo(typer.style("Deleting the CloudWatch event...", fg=typer.colors.BRIGHT_WHITE, bold=True))
        session.client("events").remove_targets(
            Rule="TheBookIsRight",
            Ids=["thebookisright"]
        )
        session.client("events").delete_rule(
            Name="TheBookIsRight"
        )
        typer.echo(typer.style("CloudWatch event deleted successfully!", fg=typer.colors.GREEN, bold=True))
    except botocore.exceptions.ClientError as err:
        typer.echo(typer.style(f'ERROR: {err.response["Error"]["Message"]}', fg=typer.colors.RED, bold=True))
        if abort_when_fail: raise typer.Exit()


if __name__ == "__main__":
    app()
