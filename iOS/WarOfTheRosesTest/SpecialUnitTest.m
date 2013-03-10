//
//  SpecialUnitTest.m
//  WarOfTheRoses
//
//  Created by Heine Skov Kristensen on 2/27/13.
//
//

#import "SpecialUnitTest.h"
#import "Definitions.h"
#import "Chariot.h"
#import "Archer.h"
#import "GameManager.h"
#import "TestHelper.h"
#import "GameBoardMockup.h"
#import "MeleeAttackAction.h"
#import "PathFinder.h"
#import "PathFinderStep.h"
#import "Berserker.h"
#import "Scout.h"
#import "Canon.h"
#import "Lancer.h"
#import "RoyalGuard.h"
#import "Pikeman.h"
#import "MovePathFinderStrategy.h"

@implementation SpecialUnitTest

- (void)setUp
{
    [super setUp];
    
    _manager = [GameManager sharedManager];
    
    _attackerFixedStrategy = [FixedDiceStrategy strategy];
    _defenderFixedStrategy = [FixedDiceStrategy strategy];
    
    _manager.attackerDiceStrategy = _attackerFixedStrategy;
    _manager.defenderDiceStrategy = _defenderFixedStrategy;
}

- (void)testChariotCanMoveAfterAttack {
    
    GameBoardMockup *mock = [[GameBoardMockup alloc] init];
    
    Archer *archer = [Archer card];
    Chariot *chariot = [Chariot card];
    
    archer.cardLocation = [GridLocation gridLocationWithRow:3 column:3];
    archer.cardColor = kCardColorRed;
    
    chariot.cardLocation = [GridLocation gridLocationWithRow:4 column:3];
    chariot.cardColor = kCardColorGreen;
    
    _manager.currentGame = [TestHelper setupGame:_manager.currentGame
                                withPlayer1Units:[NSArray arrayWithObject:chariot]
                                    player2Units:[NSArray arrayWithObjects:archer, nil]];
    
    _manager.currentPlayersTurn = kPlayerGreen;
    
    _attackerFixedStrategy.fixedDieValue = 5;
    _defenderFixedStrategy.fixedDieValue = 5;
    
    MeleeAttackAction *meleeAttack = [[MeleeAttackAction alloc] initWithPath:@[[[PathFinderStep alloc] initWithLocation:archer.cardLocation]] andCardInAction:chariot enemyCard:archer];
    
    meleeAttack.delegate = mock;
    
    [meleeAttack performActionWithCompletion:^{
        STAssertTrue(chariot.movesRemaining > 0, @"Chariot should have remaining moves after combat");
        STAssertTrue([chariot canPerformActionOfType:kActionTypeMove withRemainingActionCount:_manager.currentGame.numberOfAvailableActions], @"Chariot should be able to move after attack");
        STAssertFalse([chariot canPerformActionOfType:kActionTypeMelee withRemainingActionCount:_manager.currentGame.numberOfAvailableActions], @"Chariot shouldn't be able to attack a second time");
    }];
}

- (void)testBerserkerAttackingCannon {
    
    Berserker *berserker = [Berserker card];
    Canon *canon = [Canon card];
    
    berserker.cardLocation = [GridLocation gridLocationWithRow:3 column:2];
    berserker.cardColor = kCardColorGreen;
    
    canon.cardLocation = [GridLocation gridLocationWithRow:1 column:2];
    canon.cardColor = kCardColorRed;
    
    _manager.currentGame = [TestHelper setupGame:_manager.currentGame
                                withPlayer1Units:[NSArray arrayWithObject:berserker]
                                    player2Units:[NSArray arrayWithObjects:canon, nil]];
    
    PathFinder *pathFinder = [[PathFinder alloc] init];
    
    NSArray *meleeAttacks = [pathFinder getMeleeAttackActionsFromLocation:berserker.cardLocation forCard:berserker enemyUnits:_manager.currentGame.enemyDeck.cards allLocations:_manager.currentGame.unitLayout];
    
    STAssertTrue(meleeAttacks.count == 1, @"Berserker should be able to attack cannon");
}


- (void)testScoutCannotMoveFirstRound {
    
    Scout *scout = [Scout card];
    
    scout.cardLocation = [GridLocation gridLocationWithRow:2 column:3];
    scout.cardColor = kCardColorGreen;
        
    _manager.currentGame = [TestHelper setupGame:_manager.currentGame
                                withPlayer1Units:[NSArray arrayWithObject:scout]
                                    player2Units:[NSArray arrayWithObjects:nil]];
    
    _manager.currentPlayersTurn = kPlayerGreen;

    BOOL canPerformAction = [scout canPerformActionOfType:kActionTypeMove withRemainingActionCount:_manager.currentGame.numberOfAvailableActions];
    
    STAssertFalse(canPerformAction, @"Scout should not be able to move in the first round");
    
    [_manager endTurn];
    [_manager endTurn];
    
    canPerformAction = [scout canPerformActionOfType:kActionTypeMove withRemainingActionCount:_manager.currentGame.numberOfAvailableActions];

    STAssertTrue(canPerformAction, @"Scout should be able to move when past the first round");
}

- (void)testBerserkerCanAttackEnemyUnitWithFourNodes {
    
    Berserker *berserker = [Berserker card];
    Chariot *chariot = [Chariot card];
    Archer *archer = [Archer card];
    
    berserker.cardLocation = [GridLocation gridLocationWithRow:2 column:3];
    berserker.cardColor = kCardColorGreen;
    
    chariot.cardLocation = [GridLocation gridLocationWithRow:5 column:3];
    chariot.cardColor = kCardColorRed;
    
    archer.cardLocation = [GridLocation gridLocationWithRow:4 column:3];
    archer.cardColor = kCardColorRed;
    
    _manager.currentGame = [TestHelper setupGame:_manager.currentGame
                                withPlayer1Units:[NSArray arrayWithObject:berserker]
                                    player2Units:[NSArray arrayWithObjects:chariot, archer, nil]];
    
    _manager.currentPlayersTurn = kPlayerGreen;
    
    PathFinder *pathFinder = [[PathFinder alloc] init];
    
    NSArray *meleeAttacks = [pathFinder getMeleeAttackActionsFromLocation:berserker.cardLocation forCard:berserker enemyUnits:_manager.currentGame.enemyDeck.cards allLocations:_manager.currentGame.unitLayout];

    STAssertTrue(meleeAttacks.count == 1, @"Berserker should be able to attack chariot");
    
    NSArray *moveActions = [pathFinder getMoveActionsFromLocation:berserker.cardLocation forCard:berserker enemyUnits:_manager.currentGame.enemyDeck.cards allLocations:_manager.currentGame.unitLayout];
    
    STAssertTrue(moveActions.count == 4, @"Berserker should only be able to move to adjacent nodes");
}

- (void)testLancerGetsAttackBonusWhenAttackingWithTwoEmptyNodes {
    
    Lancer *lancer = [Lancer card];
    Archer *archer = [Archer card];
    
    lancer.cardLocation = [GridLocation gridLocationWithRow:2 column:3];
    lancer.cardColor = kCardColorGreen;
    
    archer.cardLocation = [GridLocation gridLocationWithRow:5 column:3];
    archer.cardColor = kCardColorRed;
        
    _manager.currentGame = [TestHelper setupGame:_manager.currentGame
                                withPlayer1Units:[NSArray arrayWithObject:lancer]
                                    player2Units:[NSArray arrayWithObjects:archer, nil]];
    
    _manager.currentPlayersTurn = kPlayerGreen;
    
    PathFinder *pathFinder = [[PathFinder alloc] init];
    
    NSArray *meleeAttacks = [pathFinder getMeleeAttackActionsFromLocation:lancer.cardLocation forCard:lancer enemyUnits:_manager.currentGame.enemyDeck.cards allLocations:_manager.currentGame.unitLayout];

    STAssertTrue(meleeAttacks.count == 1, @"Lancer should be able to attack archer");
    
    [lancer willPerformAction:meleeAttacks[0]];
    
    STAssertTrue([lancer.attack calculateValue].lowerValue == 3, @"Lancer should receive +2A bonus when 2 empty tiles before attack");
    STAssertTrue([lancer.attack calculateValue].upperValue == 6, @"Lancer upper attack value should remain unchanfed");
    
    [lancer didPerformedAction:meleeAttacks[0]];
    
    [_manager endTurn];
    [_manager endTurn];

    STAssertTrue([lancer.attack calculateValue].lowerValue == 5, @"Lancers +2A bonus should be removed after attack");
    STAssertTrue([lancer.attack calculateValue].upperValue == 6, @"Lancer upper attack value should remain unchanfed");
}

- (void)testLancerDoesntGetAttackBonusWhenAttackingWithLessThanTwoEmptyNodes {
    
    Lancer *lancer = [Lancer card];
    Archer *archer = [Archer card];
    
    lancer.cardLocation = [GridLocation gridLocationWithRow:2 column:3];
    lancer.cardColor = kCardColorGreen;
    
    archer.cardLocation = [GridLocation gridLocationWithRow:4 column:3];
    archer.cardColor = kCardColorRed;
    
    _manager.currentGame = [TestHelper setupGame:_manager.currentGame
                                withPlayer1Units:[NSArray arrayWithObject:lancer]
                                    player2Units:[NSArray arrayWithObjects:archer, nil]];
    
    _manager.currentPlayersTurn = kPlayerGreen;
    
    PathFinder *pathFinder = [[PathFinder alloc] init];
    
    NSArray *meleeAttacks = [pathFinder getMeleeAttackActionsFromLocation:lancer.cardLocation forCard:lancer enemyUnits:_manager.currentGame.enemyDeck.cards allLocations:_manager.currentGame.unitLayout];
    
    STAssertTrue(meleeAttacks.count == 1, @"Lancer should be able to attack archer");
    
    [lancer willPerformAction:meleeAttacks[0]];
    
    STAssertTrue([lancer.attack calculateValue].lowerValue == 5, @"Lancer shouldn't receive +2A bonus when only one empty tiles before attack");
    STAssertTrue([lancer.attack calculateValue].upperValue == 6, @"Lancer upper attack value should remain unchanfed");
    
    [lancer didPerformedAction:meleeAttacks[0]];
    
    STAssertTrue([lancer.attack calculateValue].lowerValue == 5, @"Lancers +2A bonus should be removed after attack");
    STAssertTrue([lancer.attack calculateValue].upperValue == 6, @"Lancer upper attack value should remain unchanfed");
}

- (void)testLancerDoesntGetAttackBonusWhenAttackingWithTwoNonEmptyNodes {
    
    Lancer *lancer = [Lancer card];
    Archer *archer = [Archer card];
    Archer *archer2 = [Archer card];
    
    lancer.cardLocation = [GridLocation gridLocationWithRow:2 column:3];
    lancer.cardColor = kCardColorGreen;
    
    archer.cardLocation = [GridLocation gridLocationWithRow:5 column:3];
    archer.cardColor = kCardColorRed;

    archer2.cardLocation = [GridLocation gridLocationWithRow:4 column:3];
    archer2.cardColor = kCardColorRed;

    _manager.currentGame = [TestHelper setupGame:_manager.currentGame
                                withPlayer1Units:[NSArray arrayWithObject:lancer]
                                    player2Units:[NSArray arrayWithObjects:archer,archer2, nil]];
    
    _manager.currentPlayersTurn = kPlayerGreen;
    
    PathFinder *pathFinder = [[PathFinder alloc] init];
    
    NSArray *meleeAttacks = [pathFinder getMeleeAttackActionsFromLocation:lancer.cardLocation forCard:lancer enemyUnits:_manager.currentGame.enemyDeck.cards allLocations:_manager.currentGame.unitLayout];
    
    STAssertTrue(meleeAttacks.count == 1, @"Lancer should be able to attack archer");
    
    [lancer willPerformAction:meleeAttacks[0]];
    
    STAssertTrue([lancer.attack calculateValue].lowerValue == 5, @"Lancer shouldn't receive +2A bonus when one of the two node are occupied");
    STAssertTrue([lancer.attack calculateValue].upperValue == 6, @"Lancer upper attack value should remain unchanfed");
    
    [lancer didPerformedAction:meleeAttacks[0]];
    
    STAssertTrue([lancer.attack calculateValue].lowerValue == 5, @"Lancers +2A bonus should be removed after attack");
    STAssertTrue([lancer.attack calculateValue].upperValue == 6, @"Lancer upper attack value should remain unchanfed");
}

- (void)testRoyalGuardGetsDefenseBonusAgainstMelee {
    
    RoyalGuard *royalguard = [RoyalGuard card];
    Pikeman *pikeman = [Pikeman card];
    
    royalguard.cardLocation = [GridLocation gridLocationWithRow:2 column:3];
    royalguard.cardColor = kCardColorGreen;
    
    pikeman.cardLocation = [GridLocation gridLocationWithRow:5 column:3];
    pikeman.cardColor = kCardColorRed;
        
    _manager.currentGame = [TestHelper setupGame:_manager.currentGame
                                withPlayer1Units:[NSArray arrayWithObject:royalguard]
                                    player2Units:[NSArray arrayWithObjects:pikeman, nil]];
    
    _manager.currentPlayersTurn = kPlayerGreen;
    
    [royalguard combatStartingAgainstAttacker:pikeman];
    
    STAssertTrue([royalguard.defence calculateValue].upperValue == 4, @"Royal guard should get +1D against melee attackers");
    
    [royalguard combatFinishedAgainstAttacker:pikeman withOutcome:kCombatOutcomeDefendSuccessful];

    STAssertTrue([royalguard.defence calculateValue].upperValue == 3, @"Royal guards defense bonus should be removed after combat");
}

- (void)testRoyalGuardGetsIncreasedMovementWhenMovingSideways {
    
    RoyalGuard *royalguard = [RoyalGuard card];
    
    royalguard.cardLocation = [GridLocation gridLocationWithRow:2 column:3];
    royalguard.cardColor = kCardColorGreen;
    
    _manager.currentGame = [TestHelper setupGame:_manager.currentGame
                                withPlayer1Units:[NSArray arrayWithObject:royalguard]
                                    player2Units:[NSArray arrayWithObjects:nil]];
    
    _manager.currentPlayersTurn = kPlayerGreen;

    PathFinder *pathFinder = [[PathFinder alloc] init];
    
    NSArray *pathWithSidewaysMovement = [pathFinder getPathForCard:royalguard fromGridLocation:royalguard.cardLocation toGridLocation:[GridLocation gridLocationWithRow:3 column:4] usingStrategy:[MovePathFinderStrategy strategy] allLocations:_manager.currentGame.unitLayout];
    
    STAssertTrue([royalguard allowPath:pathWithSidewaysMovement forActionType:kActionTypeMove allLocations:_manager.currentGame.unitLayout], @"RoyalGuard should be able to move 2 nodes when one of them is sideways");
}

- (void)testRoyalGuardDoesntGetIncreasedMovementWhenOnlyMovingUpOrDown {
    
    RoyalGuard *royalguard = [RoyalGuard card];
    
    royalguard.cardLocation = [GridLocation gridLocationWithRow:2 column:3];
    royalguard.cardColor = kCardColorGreen;
    
    _manager.currentGame = [TestHelper setupGame:_manager.currentGame
                                withPlayer1Units:[NSArray arrayWithObject:royalguard]
                                    player2Units:[NSArray arrayWithObjects:nil]];
    
    _manager.currentPlayersTurn = kPlayerGreen;
    
    PathFinder *pathFinder = [[PathFinder alloc] init];
    
    NSArray *pathWithoutSidewaysMovement = [pathFinder getPathForCard:royalguard fromGridLocation:royalguard.cardLocation toGridLocation:[GridLocation gridLocationWithRow:4 column:3] usingStrategy:[MovePathFinderStrategy strategy] allLocations:_manager.currentGame.unitLayout];
    
    STAssertFalse([royalguard allowPath:pathWithoutSidewaysMovement forActionType:kActionTypeMove allLocations:_manager.currentGame.unitLayout], @"RoyalGuard shouldn't be able to move 2 tiles when none of them is sideways");
}

@end
