# Generated by Django 2.0.1 on 2018-03-07 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PolicyDeck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card', models.CharField(default='', max_length=10)),
            ],
        ),
        migrations.RemoveField(
            model_name='gamestate',
            name='gameOver',
        ),
        migrations.RemoveField(
            model_name='player',
            name='previousChancellor',
        ),
        migrations.RemoveField(
            model_name='player',
            name='previousPresident',
        ),
        migrations.AddField(
            model_name='gamestate',
            name='chancellorNominated',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='gamestate',
            name='numberOfPlayers',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='hasBeenInvestigated',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='gamestate',
            name='electionTracker',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='gamestate',
            name='fasPolicyCount',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='gamestate',
            name='libPolicyCount',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='gamestate',
            name='statusID',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='chancellor',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='player',
            name='isAlive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='president',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='voting',
            name='name',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AlterField(
            model_name='voting',
            name='vote',
            field=models.BooleanField(default=False),
        ),
    ]